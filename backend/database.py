"""
Database connection and configuration for AJ Institute SATS AI Co-Pilot
Supabase PostgreSQL integration with SQLAlchemy
"""
from dotenv import load_dotenv
load_dotenv()
import os
from typing import Generator, Optional
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import logging
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration — use SQLite for local dev if no DATABASE_URL is provided
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./triage_data.db")

# SQLite needs different engine settings than PostgreSQL
sqlite_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    sqlite_kwargs = {
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    }

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False,
    **sqlite_kwargs
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

# Metadata for database operations
metadata = MetaData()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session
    Used with FastAPI's Depends() for dependency injection
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_session():
    """
    Context manager for database sessions
    Use for operations outside of FastAPI request context
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        db.close()


def test_database_connection() -> bool:
    """
    Test database connectivity
    Returns True if connection is successful, False otherwise
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            return result.fetchone()[0] == 1
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


def create_tables():
    """
    Create all tables defined in models
    This should be called during application startup
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise


def drop_tables():
    """
    Drop all tables (use with caution!)
    Only for development/testing purposes
    """
    try:
        Base.metadata.drop_all(bind=engine)
        logger.warning("All database tables dropped")
    except Exception as e:
        logger.error(f"Failed to drop database tables: {e}")
        raise


def execute_sql_file(file_path: str) -> bool:
    """
    Execute SQL commands from a file
    Useful for running schema.sql or seed data
    
    Args:
        file_path: Path to SQL file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(file_path, 'r') as file:
            sql_content = file.read()
        
        with engine.connect() as connection:
            # Split by semicolon and execute each statement
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            
            for statement in statements:
                if statement:
                    connection.execute(text(statement))
            
            connection.commit()
        
        logger.info(f"Successfully executed SQL file: {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to execute SQL file {file_path}: {e}")
        return False


def get_database_info() -> dict:
    """
    Get database connection information and statistics
    
    Returns:
        Dictionary with database information
    """
    try:
        with engine.connect() as connection:
            # Get PostgreSQL version
            version_result = connection.execute(text("SELECT version()"))
            version = version_result.fetchone()[0]
            
            # Get current database name
            db_name_result = connection.execute(text("SELECT current_database()"))
            db_name = db_name_result.fetchone()[0]
            
            # Get current user
            user_result = connection.execute(text("SELECT current_user"))
            user = user_result.fetchone()[0]
            
            # Get connection count
            conn_count_result = connection.execute(text(
                "SELECT count(*) FROM pg_stat_activity WHERE state = 'active'"
            ))
            active_connections = conn_count_result.fetchone()[0]
            
            return {
                "connected": True,
                "database_name": db_name,
                "user": user,
                "version": version,
                "active_connections": active_connections,
                "engine_pool_size": engine.pool.size(),
                "engine_pool_checked_out": engine.pool.checkedout()
            }
            
    except Exception as e:
        logger.error(f"Failed to get database info: {e}")
        return {
            "connected": False,
            "error": str(e)
        }


def check_table_exists(table_name: str) -> bool:
    """
    Check if a specific table exists in the database
    
    Args:
        table_name: Name of the table to check
        
    Returns:
        True if table exists, False otherwise
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = :table_name)"
            ), {"table_name": table_name})
            return result.fetchone()[0]
    except Exception as e:
        logger.error(f"Failed to check table existence for {table_name}: {e}")
        return False


def get_table_row_count(table_name: str) -> Optional[int]:
    """
    Get the number of rows in a specific table
    
    Args:
        table_name: Name of the table
        
    Returns:
        Number of rows or None if error
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            return result.fetchone()[0]
    except Exception as e:
        logger.error(f"Failed to get row count for {table_name}: {e}")
        return None


def backup_database_schema() -> str:
    """
    Generate SQL dump of database schema
    
    Returns:
        SQL schema as string
    """
    try:
        with engine.connect() as connection:
            # Get all table creation statements
            result = connection.execute(text("""
                SELECT 
                    'CREATE TABLE ' || schemaname || '.' || tablename || ' (' ||
                    array_to_string(
                        array_agg(
                            column_name || ' ' || data_type ||
                            case when character_maximum_length is not null 
                                 then '(' || character_maximum_length || ')' 
                                 else '' end ||
                            case when is_nullable = 'NO' then ' NOT NULL' else '' end
                        ), ', '
                    ) || ');'
                FROM information_schema.tables t
                JOIN information_schema.columns c ON c.table_name = t.tablename
                WHERE t.schemaname = 'public'
                GROUP BY schemaname, tablename
            """))
            
            schema_statements = [row[0] for row in result.fetchall()]
            return '\n\n'.join(schema_statements)
            
    except Exception as e:
        logger.error(f"Failed to backup database schema: {e}")
        return ""


# Database health check function for FastAPI health endpoint
async def database_health_check() -> dict:
    """
    Async health check for database connectivity
    Used in FastAPI health check endpoint
    
    Returns:
        Dictionary with health status
    """
    try:
        # Test basic connectivity
        connected = test_database_connection()
        
        if connected:
            # Get additional info
            info = get_database_info()
            return {
                "status": "healthy",
                "database": info.get("database_name", "unknown"),
                "active_connections": info.get("active_connections", 0)
            }
        else:
            return {
                "status": "unhealthy",
                "error": "Cannot connect to database"
            }
            
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


# Initialize database on module import
if __name__ == "__main__":
    # Test database connection
    print("Testing database connection...")
    if test_database_connection():
        print("✅ Database connection successful")
        
        # Print database info
        info = get_database_info()
        print(f"Database: {info.get('database_name')}")
        print(f"User: {info.get('user')}")
        print(f"Active connections: {info.get('active_connections')}")
        
        # Check if main tables exist
        tables_to_check = ['users', 'cases', 'audit_log']
        for table in tables_to_check:
            exists = check_table_exists(table)
            status = "✅" if exists else "❌"
            print(f"{status} Table '{table}': {'exists' if exists else 'missing'}")
            
            if exists:
                count = get_table_row_count(table)
                print(f"   Rows: {count}")
    else:
        print("❌ Database connection failed")
        print("Please check your DATABASE_URL or SUPABASE_URL environment variable")