$ErrorActionPreference='Continue'
"=== SiliconFlow /v1/models 是否免鉴权可读 ==="
try {
  $r = Invoke-RestMethod -Uri 'https://api.siliconflow.cn/v1/models' -Method Get -TimeoutSec 40
  $ids = $r.data | Select-Object -ExpandProperty id
  "  可读，共 $($ids.Count) 个模型"
  "  ---- 含 VL / VL 相关 ----"
  $ids | Where-Object { $_ -match 'VL|vl|vision|Vision|OCR' } | ForEach-Object { "    " + $_ }
} catch {
  $code='n/a'; if($_.Exception.Response){$code=[int]$_.Exception.Response.StatusCode}
  "  读取失败 $code : " + ($_.ErrorDetails.Message)
}
