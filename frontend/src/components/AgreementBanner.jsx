import React from 'react'

const AgreementBanner = ({ result }) => {
  if (!result) return null

  const isAgreement = result.nurse_category === result.ai_recommendation
  
  return (
    <div className={`mb-6 p-4 rounded-lg border-2 ${
      isAgreement 
        ? 'bg-green-50 border-green-200' 
        : 'bg-orange-50 border-orange-200'
    }`}>
      <div className="flex items-center">
        <div className="flex-shrink-0">
          {isAgreement ? (
            <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          ) : (
            <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          )}
        </div>
        <div className="ml-3">
          <h3 className={`text-lg font-semibold ${
            isAgreement ? 'text-green-800' : 'text-orange-800'
          }`}>
            {isAgreement ? '✅ Agreement' : '⚠️ Discrepancy Detected'}
          </h3>
          <p className={`text-sm ${
            isAgreement ? 'text-green-700' : 'text-orange-700'
          }`}>
            {isAgreement 
              ? `Nurse and AI both recommend ${result.nurse_category} triage category`
              : `Nurse assessment: ${result.nurse_category} | AI recommendation: ${result.ai_recommendation}`
            }
          </p>
          {!isAgreement && (
            <p className="text-xs text-orange-600 mt-1">
              Please review the case details and consider the AI analysis before final decision.
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

export default AgreementBanner