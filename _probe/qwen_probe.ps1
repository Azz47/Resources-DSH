$ErrorActionPreference = 'Continue'
$ep = 'https://oai.endpoints.kepler.ai.cloud.ovh.net/v1'
$hdr = @{ 'Content-Type' = 'application/json' }
$img = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=='

"=== 1) GET /models (which Qwen models this endpoint serves) ==="
try {
  $m = Invoke-RestMethod -Uri "$ep/models" -Method Get -TimeoutSec 30
  $m.data | ForEach-Object { "  " + $_.id }
} catch { "  FAIL: " + $_.Exception.Message }

function Probe([string]$label, [string]$model, [hashtable]$extra) {
  $body = @{
    model = $model
    max_tokens = 24
    messages = @(@{ role='user'; content = @(
      @{ type='text'; text='Reply with the single word: red' },
      @{ type='image_url'; image_url = @{ url=$img } }
    )})
  }
  foreach ($k in $extra.Keys) { $body[$k] = $extra[$k] }
  $json = $body | ConvertTo-Json -Depth 12 -Compress
  try {
    $r = Invoke-RestMethod -Uri "$ep/chat/completions" -Method Post -Headers $hdr -Body $json -TimeoutSec 60
    "  OK    | $label -> " + ($r.choices[0].message.content -replace "`r?`n",' ')
  } catch {
    $code = 'n/a'; if ($_.Exception.Response) { $code = [int]$_.Exception.Response.StatusCode }
    $msg = $_.ErrorDetails.Message; if (-not $msg) { $msg = $_.Exception.Message }
    "  FAIL  | $label -> $code " + ($msg -replace "`r?`n",' ')
  }
}

$models = @('Qwen2.5-VL-72B-Instruct','Qwen3.5-397B-A17B','Qwen3.5-9B','Qwen3.6-27B','Mistral-Small-3.2-24B-Instruct-2506')

""
"=== 2) 不带 prompt_cache_key（期望 200） ==="
foreach ($mm in $models) { Probe $mm $mm @{} }

""
"=== 3) 带 prompt_cache_key（验证根因） ==="
Probe 'Qwen2.5-VL-72B-Instruct' 'Qwen2.5-VL-72B-Instruct' @{ prompt_cache_key = 'probe-abc' }
