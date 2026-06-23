# Financial Risk Management - Demo Script (PowerShell)
# Demonstrates end-to-end workflow with live API calls

# Configuration
$API_BASE_URL = "https://financial-risk-api.2b4ptlu9b878.eu-de.codeengine.appdomain.cloud"
$DEMO_ACCOUNT_ID = "ACC-12345"

# Helper Functions
function Write-Header {
    param([string]$Text)
    Write-Host "`n" -NoNewline
    Write-Host ("=" * 80) -ForegroundColor Magenta
    Write-Host $Text.PadLeft(40 + $Text.Length / 2).PadRight(80) -ForegroundColor Magenta
    Write-Host ("=" * 80) -ForegroundColor Magenta
    Write-Host ""
}

function Write-Step {
    param([int]$StepNum, [string]$Text)
    Write-Host "[STEP $StepNum] " -ForegroundColor Cyan -NoNewline
    Write-Host $Text
}

function Write-Success {
    param([string]$Text)
    Write-Host "✓ $Text" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Text)
    Write-Host "⚠ $Text" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Text)
    Write-Host "✗ $Text" -ForegroundColor Red
}

function Invoke-ApiCall {
    param(
        [string]$Endpoint,
        [string]$Method = "GET",
        [hashtable]$Body = $null
    )
    
    $url = "$API_BASE_URL$Endpoint"
    
    try {
        $params = @{
            Uri = $url
            Method = $Method
            ContentType = "application/json"
            TimeoutSec = 10
        }
        
        if ($Body) {
            $params.Body = ($Body | ConvertTo-Json -Depth 10)
        }
        
        $response = Invoke-RestMethod @params
        return $response
    }
    catch {
        Write-Error "API call failed: $_"
        return @{ error = $_.Exception.Message }
    }
}

function Show-HealthCheck {
    Write-Step 1 "Health Check - Verifying API Status"
    Write-Host "   Endpoint: GET $API_BASE_URL/health`n"
    
    $result = Invoke-ApiCall -Endpoint "/health"
    
    if (-not $result.error) {
        Write-Success "API is healthy!"
        Write-Host "   Status: $($result.status)"
        Write-Host "   Data Layer: $($result.data_layer_status)"
        Write-Host "   Total Transactions: $($result.total_transactions)"
        Write-Host "   Timestamp: $($result.timestamp)"
    }
    else {
        Write-Error "Health check failed!"
    }
    
    return $result
}

function Show-RiskAssessment {
    param([string]$AccountId)
    
    Write-Step 2 "Risk Assessment - Analyzing Account $AccountId"
    Write-Host "   Endpoint: POST $API_BASE_URL/api/v1/assess/risk`n"
    
    $payload = @{ account_id = $AccountId }
    Write-Host "   Request:"
    Write-Host ($payload | ConvertTo-Json) -ForegroundColor Blue
    Write-Host ""
    
    $result = Invoke-ApiCall -Endpoint "/api/v1/assess/risk" -Method "POST" -Body $payload
    
    if (-not $result.error) {
        Write-Success "Risk assessment completed!"
        Write-Host "   Risk Score: $($result.risk_score)"
        Write-Host "   Risk Level: $($result.risk_level)"
        
        if ($result.risk_factors) {
            Write-Host "   Risk Factors:"
            $result.risk_factors.PSObject.Properties | ForEach-Object {
                Write-Host "      - $($_.Name): $($_.Value)"
            }
        }
        
        if ($result.high_risk_accounts) {
            Write-Host "   High Risk Accounts: $($result.high_risk_accounts.Count)"
        }
    }
    else {
        Write-Error "Risk assessment failed!"
    }
    
    return $result
}

function Show-FraudDetection {
    param([string]$AccountId)
    
    Write-Step 3 "Fraud Detection - Scanning Account $AccountId"
    Write-Host "   Endpoint: POST $API_BASE_URL/api/v1/detect/fraud`n"
    
    $payload = @{ 
        account_id = $AccountId
        mode = "account_profile"
    }
    Write-Host "   Request:"
    Write-Host ($payload | ConvertTo-Json) -ForegroundColor Blue
    Write-Host ""
    
    $result = Invoke-ApiCall -Endpoint "/api/v1/detect/fraud" -Method "POST" -Body $payload
    
    if (-not $result.error) {
        Write-Success "Fraud detection completed!"
        
        if ($result.fraud_signals) {
            $signals = $result.fraud_signals
            Write-Host "   Fraud Signals:"
            Write-Host "      - Temporal Anomalies: $($signals.temporal_anomalies)"
            Write-Host "      - Laundering History: $($signals.laundering_history)"
            Write-Host "      - Suspicious Patterns: $($signals.suspicious_patterns)"
        }
        
        if ($result.account_profile) {
            $profile = $result.account_profile
            Write-Host "   Account Profile:"
            Write-Host "      - Total Transactions: $($profile.total_transactions)"
            Write-Host "      - Total Amount: `$$($profile.total_amount)"
            Write-Host "      - Average Transaction: `$$($profile.avg_transaction)"
        }
    }
    else {
        Write-Error "Fraud detection failed!"
    }
    
    return $result
}

function Show-TransactionAnalysis {
    param([string]$AccountId)
    
    Write-Step 4 "Transaction Analysis - Detecting AML Patterns for $AccountId"
    Write-Host "   Endpoint: POST $API_BASE_URL/api/v1/analyze/transaction`n"
    
    $payload = @{ account_id = $AccountId }
    Write-Host "   Request:"
    Write-Host ($payload | ConvertTo-Json) -ForegroundColor Blue
    Write-Host ""
    
    $result = Invoke-ApiCall -Endpoint "/api/v1/analyze/transaction" -Method "POST" -Body $payload
    
    if (-not $result.error) {
        Write-Success "Transaction analysis completed!"
        
        if ($result.patterns_detected) {
            Write-Host "   AML Patterns Detected:"
            $result.patterns_detected.PSObject.Properties | ForEach-Object {
                $status = if ($_.Value) { "✓ DETECTED" } else { "✗ Not detected" }
                $color = if ($_.Value) { "Yellow" } else { "Green" }
                Write-Host "      - $($_.Name): " -NoNewline
                Write-Host $status -ForegroundColor $color
            }
        }
        
        if ($result.transaction_stats) {
            $stats = $result.transaction_stats
            Write-Host "   Transaction Statistics:"
            Write-Host "      - Total Transactions: $($stats.total_transactions)"
            Write-Host "      - Total Amount: `$$($stats.total_amount)"
            Write-Host "      - Average Amount: `$$($stats.avg_amount)"
        }
    }
    else {
        Write-Error "Transaction analysis failed!"
    }
    
    return $result
}

function Show-Recommendations {
    param(
        [double]$RiskScore,
        [hashtable]$Patterns,
        [hashtable]$FraudSignals
    )
    
    Write-Step 5 "Recommendation Generation - Creating Action Plan"
    Write-Host "   Endpoint: POST $API_BASE_URL/api/v1/recommend/actions`n"
    
    $payload = @{
        risk_score = $RiskScore
        patterns = $Patterns
        fraud_signals = $FraudSignals
    }
    Write-Host "   Request:"
    Write-Host ($payload | ConvertTo-Json -Depth 5) -ForegroundColor Blue
    Write-Host ""
    
    $result = Invoke-ApiCall -Endpoint "/api/v1/recommend/actions" -Method "POST" -Body $payload
    
    if (-not $result.error) {
        Write-Success "Recommendations generated!"
        
        if ($result.recommended_actions) {
            Write-Host "   Recommended Actions ($($result.recommended_actions.Count)):"
            $i = 1
            foreach ($action in $result.recommended_actions) {
                $actionType = $action.action
                $priority = $action.priority
                $reasoning = $action.reasoning
                
                $color = switch ($actionType) {
                    "ALERT" { "Red" }
                    "REVIEW" { "Yellow" }
                    "BLOCK" { "Red" }
                    default { "Cyan" }
                }
                
                Write-Host "      $i. " -NoNewline
                Write-Host $actionType -ForegroundColor $color -NoNewline
                Write-Host " (Priority: $priority)"
                Write-Host "         Reasoning: $reasoning"
                $i++
            }
        }
    }
    else {
        Write-Error "Recommendation generation failed!"
    }
    
    return $result
}

function Show-Explanation {
    param(
        [double]$RiskScore,
        [array]$Patterns,
        [array]$FraudSignals
    )
    
    Write-Step 6 "Explanation Generation - IBM watsonx.ai Granite LLM"
    Write-Host "   Endpoint: POST $API_BASE_URL/api/v1/explain`n"
    
    $payload = @{
        risk_score = $RiskScore
        patterns = $Patterns
        fraud_signals = $FraudSignals
    }
    Write-Host "   Request:"
    Write-Host ($payload | ConvertTo-Json -Depth 5) -ForegroundColor Blue
    Write-Host ""
    
    $result = Invoke-ApiCall -Endpoint "/api/v1/explain" -Method "POST" -Body $payload
    
    if (-not $result.error) {
        Write-Success "Explanation generated!"
        Write-Host "   Model Used: $($result.model_used)"
        Write-Host "   Fallback Used: $($result.fallback_used)"
        Write-Host "`n   Explanation:" -ForegroundColor White
        Write-Host "   $($result.explanation)"
    }
    else {
        Write-Error "Explanation generation failed!"
    }
    
    return $result
}

function Show-ConsolidatedReport {
    param(
        [hashtable]$Health,
        [hashtable]$Risk,
        [hashtable]$Fraud,
        [hashtable]$Transaction,
        [hashtable]$Recommendations,
        [hashtable]$Explanation
    )
    
    Write-Header "CONSOLIDATED FINANCIAL RISK ANALYSIS REPORT"
    
    Write-Host "Report Generated: " -NoNewline
    Write-Host (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
    Write-Host "Account ID: $DEMO_ACCOUNT_ID"
    Write-Host "API Endpoint: $API_BASE_URL"
    Write-Host ""
    
    # System Status
    Write-Host "1. SYSTEM STATUS" -ForegroundColor White
    Write-Host "   Status: $($Health.status)"
    Write-Host "   Data Layer: $($Health.data_layer_status)"
    Write-Host "   Total Transactions Available: $($Health.total_transactions)"
    Write-Host ""
    
    # Risk Assessment
    Write-Host "2. RISK ASSESSMENT" -ForegroundColor White
    $riskScore = $Risk.risk_score
    $riskLevel = $Risk.risk_level
    
    $riskColor = switch ($riskLevel) {
        "HIGH" { "Red" }
        "MEDIUM" { "Yellow" }
        default { "Green" }
    }
    
    Write-Host "   Risk Score: " -NoNewline
    Write-Host $riskScore -ForegroundColor $riskColor
    Write-Host "   Risk Level: " -NoNewline
    Write-Host $riskLevel -ForegroundColor $riskColor
    
    if ($Risk.risk_factors) {
        Write-Host "   Risk Factors:"
        $Risk.risk_factors.PSObject.Properties | ForEach-Object {
            Write-Host "      - $($_.Name): $($_.Value)"
        }
    }
    Write-Host ""
    
    # Fraud Detection
    Write-Host "3. FRAUD DETECTION" -ForegroundColor White
    if ($Fraud.fraud_signals) {
        $signals = $Fraud.fraud_signals
        Write-Host "   Temporal Anomalies: $($signals.temporal_anomalies)"
        Write-Host "   Laundering History: $($signals.laundering_history)"
        Write-Host "   Suspicious Patterns: $($signals.suspicious_patterns)"
    }
    Write-Host ""
    
    # Transaction Analysis
    Write-Host "4. TRANSACTION ANALYSIS" -ForegroundColor White
    if ($Transaction.patterns_detected) {
        $detectedPatterns = @()
        $Transaction.patterns_detected.PSObject.Properties | ForEach-Object {
            if ($_.Value) {
                $detectedPatterns += $_.Name
            }
        }
        
        if ($detectedPatterns.Count -gt 0) {
            Write-Host "   AML Patterns Detected:" -ForegroundColor Yellow
            foreach ($pattern in $detectedPatterns) {
                Write-Host "      - $pattern"
            }
        }
        else {
            Write-Host "   No AML patterns detected" -ForegroundColor Green
        }
    }
    
    if ($Transaction.transaction_stats) {
        $stats = $Transaction.transaction_stats
        Write-Host "   Transaction Statistics:"
        Write-Host "      - Total: $($stats.total_transactions)"
        Write-Host "      - Total Amount: `$$($stats.total_amount)"
        Write-Host "      - Average: `$$($stats.avg_amount)"
    }
    Write-Host ""
    
    # Recommendations
    Write-Host "5. RECOMMENDED ACTIONS" -ForegroundColor White
    if ($Recommendations.recommended_actions) {
        $i = 1
        foreach ($action in $Recommendations.recommended_actions) {
            $actionType = $action.action
            $priority = $action.priority
            
            $color = switch ($actionType) {
                "ALERT" { "Red" }
                "REVIEW" { "Yellow" }
                "BLOCK" { "Red" }
                default { "Cyan" }
            }
            
            Write-Host "   $i. " -NoNewline
            Write-Host $actionType -ForegroundColor $color -NoNewline
            Write-Host " (Priority: $priority)"
            $i++
        }
    }
    Write-Host ""
    
    # Explanation
    Write-Host "6. EXPLANATION (IBM watsonx.ai Granite)" -ForegroundColor White
    if ($Explanation.explanation) {
        Write-Host "   $($Explanation.explanation)"
        Write-Host "`n   Model: $($Explanation.model_used)"
    }
    Write-Host ""
    
    Write-Host ("=" * 80) -ForegroundColor Magenta
}

# Main Demo
function Start-Demo {
    Write-Header "FINANCIAL RISK MANAGEMENT SYSTEM - LIVE DEMO"
    Write-Host "IBM Open Agentic Builders - Track A: Financial Risk Management" -ForegroundColor White
    Write-Host "Demo Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    Write-Host "API Endpoint: $API_BASE_URL"
    Write-Host "Demo Account: $DEMO_ACCOUNT_ID"
    Write-Host ""
    
    Write-Host "Press Enter to start the demo..." -ForegroundColor Cyan
    Read-Host
    
    # Step 1: Health Check
    $healthResult = Show-HealthCheck
    Start-Sleep -Seconds 1
    
    # Step 2: Risk Assessment
    $riskResult = Show-RiskAssessment -AccountId $DEMO_ACCOUNT_ID
    Start-Sleep -Seconds 1
    
    # Step 3: Fraud Detection
    $fraudResult = Show-FraudDetection -AccountId $DEMO_ACCOUNT_ID
    Start-Sleep -Seconds 1
    
    # Step 4: Transaction Analysis
    $transactionResult = Show-TransactionAnalysis -AccountId $DEMO_ACCOUNT_ID
    Start-Sleep -Seconds 1
    
    # Step 5: Recommendations
    $riskScore = if ($riskResult.risk_score) { $riskResult.risk_score } else { 0.5 }
    $patterns = if ($transactionResult.patterns_detected) { $transactionResult.patterns_detected } else { @{} }
    $fraudSignals = if ($fraudResult.fraud_signals) { $fraudResult.fraud_signals } else { @{} }
    
    $recommendationsResult = Show-Recommendations -RiskScore $riskScore -Patterns $patterns -FraudSignals $fraudSignals
    Start-Sleep -Seconds 1
    
    # Step 6: Explanation
    $patternsList = @()
    if ($patterns) {
        $patterns.PSObject.Properties | ForEach-Object {
            if ($_.Value) {
                $patternsList += $_.Name
            }
        }
    }
    
    $fraudList = @()
    if ($fraudSignals) {
        $fraudSignals.PSObject.Properties | ForEach-Object {
            if ($_.Value) {
                $fraudList += $_.Name
            }
        }
    }
    
    $explanationResult = Show-Explanation -RiskScore $riskScore -Patterns $patternsList -FraudSignals $fraudList
    Start-Sleep -Seconds 1
    
    # Generate Consolidated Report
    Show-ConsolidatedReport -Health $healthResult -Risk $riskResult -Fraud $fraudResult `
        -Transaction $transactionResult -Recommendations $recommendationsResult -Explanation $explanationResult
    
    Write-Host "`n✓ Demo completed successfully!" -ForegroundColor Green
    Write-Host "`nNext Steps:" -ForegroundColor Cyan
    Write-Host "   1. Review the consolidated report above"
    Write-Host "   2. Test with different account IDs"
    Write-Host "   3. Explore watsonx Orchestrate UI for agent orchestration"
    Write-Host "   4. Check API documentation at $API_BASE_URL/docs"
    Write-Host ""
}

# Run the demo
try {
    Start-Demo
}
catch {
    Write-Error "Demo failed with error: $_"
    exit 1
}

# Made with Bob
