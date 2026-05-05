param(
  [string]$TemplatePath = "C:\Users\tukum\Downloads\reopt-pysam\reports\decks\conformance\template\allotrope-template.pptx",
  [string]$OutputPath = "C:\Users\tukum\Downloads\reopt-pysam\reports\decks\2026-04-21-dppa-case-3-allotrope.pptx",
  [string]$PreviewDir = "C:\Users\tukum\Downloads\reopt-pysam\artifacts\case3-allotrope-preview"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function OleColor {
  param([int]$r, [int]$g, [int]$b)
  return $r + (256 * $g) + (65536 * $b)
}

function Set-Text {
  param(
    $Shape,
    [string]$Text,
    [double]$Size = 0,
    [int]$Bold = -2,
    [int]$Color = -1,
    [int]$ParagraphAlignment = -1
  )

  $Shape.TextFrame.TextRange.Text = $Text
  if ($Size -gt 0) {
    $Shape.TextFrame.TextRange.Font.Size = $Size
  }
  if ($Bold -ne -2) {
    $Shape.TextFrame.TextRange.Font.Bold = $Bold
  }
  if ($Color -ge 0) {
    $Shape.TextFrame.TextRange.Font.Color.RGB = $Color
  }
  if ($ParagraphAlignment -ge 0) {
    $Shape.TextFrame.TextRange.ParagraphFormat.Alignment = $ParagraphAlignment
  }
}

function Add-CoverPanel {
  param($Slide, [double]$Left, [double]$Top, [double]$Width, [double]$Height)
  $panel = $Slide.Shapes.AddShape(1, $Left, $Top, $Width, $Height)
  $panel.Fill.ForeColor.RGB = OleColor 255 255 255
  $panel.Fill.Transparency = 0.08
  $panel.Line.Visible = 0
  $panel.Shadow.Visible = 0
  $panel.ZOrder(0) | Out-Null
  return $panel
}

function Add-RoundedPanel {
  param(
    $Slide,
    [double]$Left,
    [double]$Top,
    [double]$Width,
    [double]$Height,
    [int]$FillColor,
    [double]$Transparency = 0.0
  )
  $shape = $Slide.Shapes.AddShape(5, $Left, $Top, $Width, $Height)
  $shape.Fill.ForeColor.RGB = $FillColor
  $shape.Fill.Transparency = $Transparency
  $shape.Line.Visible = 0
  $shape.Shadow.Visible = 0
  $shape.ZOrder(0) | Out-Null
  return $shape
}

function Add-PlainRect {
  param(
    $Slide,
    [double]$Left,
    [double]$Top,
    [double]$Width,
    [double]$Height,
    [int]$FillColor,
    [double]$Transparency = 0.0,
    [int]$LineColor = -1
  )
  $shape = $Slide.Shapes.AddShape(1, $Left, $Top, $Width, $Height)
  $shape.Fill.ForeColor.RGB = $FillColor
  $shape.Fill.Transparency = $Transparency
  if ($LineColor -ge 0) {
    $shape.Line.Visible = -1
    $shape.Line.ForeColor.RGB = $LineColor
    $shape.Line.Weight = 0.75
  } else {
    $shape.Line.Visible = 0
  }
  $shape.Shadow.Visible = 0
  $shape.ZOrder(0) | Out-Null
  return $shape
}

function Add-TextBox {
  param(
    $Slide,
    [double]$Left,
    [double]$Top,
    [double]$Width,
    [double]$Height,
    [string]$Text,
    [double]$Size,
    [int]$Bold,
    [int]$Color,
    [int]$Alignment = 1
  )
  $shape = $Slide.Shapes.AddTextbox(1, $Left, $Top, $Width, $Height)
  $shape.TextFrame.WordWrap = -1
  $shape.TextFrame.AutoSize = 0
  $shape.TextFrame.MarginLeft = 2
  $shape.TextFrame.MarginRight = 2
  $shape.TextFrame.MarginTop = 2
  $shape.TextFrame.MarginBottom = 2
  $shape.TextFrame.TextRange.Font.Name = "Cabin"
  Set-Text -Shape $shape -Text $Text -Size $Size -Bold $Bold -Color $Color -ParagraphAlignment $Alignment
  $shape.Line.Visible = 0
  $shape.Fill.Visible = 0
  return $shape
}

function Set-TableCell {
  param(
    $Table,
    [int]$Row,
    [int]$Column,
    [string]$Text,
    [double]$Size = 12,
    [int]$Bold = 0,
    [int]$Color = -1,
    [int]$Alignment = 1
  )
  $cell = $Table.Cell($Row, $Column).Shape
  $cell.TextFrame.TextRange.Text = $Text
  $cell.TextFrame.TextRange.Font.Name = "Cabin"
  $cell.TextFrame.TextRange.Font.Size = $Size
  $cell.TextFrame.TextRange.Font.Bold = $Bold
  if ($Color -ge 0) {
    $cell.TextFrame.TextRange.Font.Color.RGB = $Color
  }
  $cell.TextFrame.TextRange.ParagraphFormat.Alignment = $Alignment
}

function Add-TableTitle {
  param(
    $Slide,
    [double]$Left,
    [double]$Top,
    [double]$Width,
    [double]$Height,
    [string]$Text
  )
  $shape = Add-PlainRect -Slide $Slide -Left $Left -Top $Top -Width $Width -Height $Height -FillColor (OleColor 31 50 77)
  $tb = Add-TextBox -Slide $Slide -Left ($Left + 4) -Top ($Top + 1) -Width ($Width - 8) -Height ($Height - 2) -Text $Text -Size 10 -Bold -1 -Color (OleColor 255 255 255)
  return @($shape, $tb)
}

$greenDark = OleColor 21 91 85
$greenMid = OleColor 32 120 109
$greenSoft = OleColor 181 216 208
$greenTint = OleColor 215 236 232
$greenAccent = OleColor 56 118 29
$ink = OleColor 34 34 34
$gray = OleColor 102 102 102
$navy = OleColor 31 50 77
$white = OleColor 255 255 255
$failRed = OleColor 192 0 0

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $OutputPath) | Out-Null
New-Item -ItemType Directory -Force -Path $PreviewDir | Out-Null
Copy-Item -LiteralPath $TemplatePath -Destination $OutputPath -Force

$ppt = New-Object -ComObject PowerPoint.Application
$presentation = $ppt.Presentations.Open($OutputPath, $false, $false, $false)

try {
  $slide1 = $presentation.Slides.Item(1)
  Set-Text -Shape $slide1.Shapes.Item(2) -Text "Allotrope Vietnam DPPA Case 3`rSaigon18 Bridge Final Decision`rApril 2026"

  $slide2 = $presentation.Slides.Item(2)
  Set-Text -Shape $slide2.Shapes.Item(1) -Text "DPPA Case 3:`rFinal Decision Summary"
  $slide2.Shapes.Item(2).Delete()
  Add-PlainRect -Slide $slide2 -Left 23 -Top 100 -Width 665 -Height 232 -FillColor $white | Out-Null
  $table2 = $slide2.Shapes.AddTable(7, 3, 23, 100, 665, 232).Table
  $summaryRows = @(
    @("Decision Gate", "Current Result", "Readout"),
    @("Buyer gate", "FAIL", "+2.9B VND/yr vs EVN baseline"),
    @("Developer gate", "FAIL", "Min DSCR -0.175; after-tax NPV -`$6.05M"),
    @("Physical sizing", "4.8 MW PV + 1.5 MW / 3.3 MWh BESS", "Bounded-opt solution sits at upper bounds"),
    @("Matched renewable", "6.84 GWh/yr", "Only 3.7% of the 184.3 GWh annual load"),
    @("All-in PPA rate", "2,334 VND/kWh", "~3,900+ VND/kWh needed to clear DSCR >= 1.0"),
    @("Recommendation", "REJECT CURRENT CASE", "Reopen strike, resize, and validate with real 8760 data")
  )
  for ($r = 1; $r -le $summaryRows.Count; $r++) {
    for ($c = 1; $c -le 3; $c++) {
      $isHeader = $r -eq 1
      $isFail = ($summaryRows[$r - 1][$c - 1] -eq "FAIL")
      Set-TableCell -Table $table2 -Row $r -Column $c -Text $summaryRows[$r - 1][$c - 1] -Size ($(if ($isHeader) { 12 } else { 10.5 })) -Bold ($(if ($isHeader -or $c -eq 1 -or $isFail) { -1 } else { 0 })) -Color ($(if ($isHeader) { $white } elseif ($isFail) { $failRed } else { $ink })) -Alignment 1
    }
  }
  $table2.Cell(1,1).Shape.Fill.ForeColor.RGB = $greenDark
  $table2.Cell(1,2).Shape.Fill.ForeColor.RGB = $greenDark
  $table2.Cell(1,3).Shape.Fill.ForeColor.RGB = $greenDark

  $slide3 = $presentation.Slides.Item(3)
  Set-Text -Shape $slide3.Shapes.Item(6) -Text "CASE INFORMATION"
  $slide3.Shapes.Item(7).Delete()
  Add-PlainRect -Slide $slide3 -Left 18 -Top 72 -Width 347 -Height 316 -FillColor $white | Out-Null
  $table3 = $slide3.Shapes.AddTable(6, 2, 20, 74, 340, 286).Table
  $caseInfo = @(
    @("Case Type", "Synthetic financial DPPA bridge case"),
    @("Data Basis", "Saigon18 load + CFMP/FMP + tariff from same workstream"),
    @("Load / Strike", "184.26 GWh/yr proxy load; strike = 1,809.61 VND/kWh"),
    @("Tariff Branches", "Legacy TOU reference plus 22kV two-part realism branch"),
    @("Bounded Result", "PV 4.8 MW; BESS 1.5 MW / 3.3 MWh"),
    @("Decision Gate", "Buyer FAIL and developer FAIL; real 8760 load still needed")
  )
  for ($r = 1; $r -le $caseInfo.Count; $r++) {
    Set-TableCell -Table $table3 -Row $r -Column 1 -Text $caseInfo[$r - 1][0] -Size 10.8 -Bold -1 -Color $ink
    Set-TableCell -Table $table3 -Row $r -Column 2 -Text $caseInfo[$r - 1][1] -Size 10.3 -Bold 0 -Color $ink
  }
  Add-PlainRect -Slide $slide3 -Left 382 -Top 86 -Width 323 -Height 310 -FillColor $white | Out-Null
  Add-RoundedPanel -Slide $slide3 -Left 406 -Top 104 -Width 275 -Height 40 -FillColor $greenMid | Out-Null
  Add-TextBox -Slide $slide3 -Left 420 -Top 112 -Width 248 -Height 22 -Text "Case Basis Snapshot" -Size 18 -Bold -1 -Color $white | Out-Null
  Add-RoundedPanel -Slide $slide3 -Left 420 -Top 160 -Width 246 -Height 48 -FillColor $greenTint | Out-Null
  Add-TextBox -Slide $slide3 -Left 434 -Top 170 -Width 220 -Height 32 -Text "184.3 GWh annual proxy load" -Size 17 -Bold -1 -Color $greenDark | Out-Null
  Add-RoundedPanel -Slide $slide3 -Left 420 -Top 220 -Width 246 -Height 48 -FillColor $greenTint | Out-Null
  Add-TextBox -Slide $slide3 -Left 434 -Top 230 -Width 220 -Height 32 -Text "6.84 GWh matched renewable output" -Size 17 -Bold -1 -Color $greenDark | Out-Null
  Add-RoundedPanel -Slide $slide3 -Left 420 -Top 280 -Width 246 -Height 48 -FillColor $greenTint | Out-Null
  Add-TextBox -Slide $slide3 -Left 434 -Top 290 -Width 220 -Height 32 -Text "2 tariff branches; same-site data basis confirmed" -Size 15 -Bold -1 -Color $greenDark | Out-Null
  Add-RoundedPanel -Slide $slide3 -Left 420 -Top 340 -Width 246 -Height 40 -FillColor $greenSoft | Out-Null
  Add-TextBox -Slide $slide3 -Left 434 -Top 348 -Width 220 -Height 22 -Text "Buyer and developer gates both fail at current strike" -Size 13 -Bold -1 -Color $ink | Out-Null
  Add-PlainRect -Slide $slide3 -Left 18 -Top 384 -Width 350 -Height 16 -FillColor $white | Out-Null

  $slide4 = $presentation.Slides.Item(4)
  Set-Text -Shape $slide4.Shapes.Item(3) -Text "CONCLUSIONS & RECOMMENDATIONS"
  $cardTitles = @(
    "Buyer Cost Fails",
    "Developer Finance Fails",
    "Bounded Minimum Is Still Uneconomic",
    "Renewable Coverage Is Too Thin",
    "Reopen Strike, Sizing, and Data"
  )
  $cardBodies = @(
    "The buyer pays 353.9B VND/yr under DPPA settlement versus 351.0B VND/yr under the EVN counterfactual, so the case loses on direct bill impact.",
    "At 2,334 VND/kWh all-in revenue, the project covers only about 59% of annual debt service and screens at -`$6.05M NPV with min DSCR -0.175.",
    "REopt found the buyer-side minimum inside the allowed PV and BESS bounds, but that minimum still does not beat the EVN baseline or unlock finance.",
    "Only 6.84 GWh of renewable delivery serves a 184.26 GWh load. The remaining 177.4 GWh stays on EVN imports, so the DPPA premium never scales.",
    "Next pass should run a strike sweep, relax or resize the storage-constrained build, and replace the static proxy with actual 8760 project load data."
  )
  Set-Text -Shape $slide4.Shapes.Item(15) -Text $cardTitles[0]
  Set-Text -Shape $slide4.Shapes.Item(16) -Text $cardTitles[1]
  Set-Text -Shape $slide4.Shapes.Item(17) -Text $cardTitles[2]
  Set-Text -Shape $slide4.Shapes.Item(18) -Text $cardTitles[3]
  Set-Text -Shape $slide4.Shapes.Item(19) -Text $cardTitles[4]
  Set-Text -Shape $slide4.Shapes.Item(20) -Text $cardBodies[0] -Size 11.2
  Set-Text -Shape $slide4.Shapes.Item(21) -Text $cardBodies[1] -Size 11.1
  Set-Text -Shape $slide4.Shapes.Item(22) -Text $cardBodies[2] -Size 10.7
  Set-Text -Shape $slide4.Shapes.Item(23) -Text $cardBodies[3] -Size 10.9
  Set-Text -Shape $slide4.Shapes.Item(24) -Text $cardBodies[4] -Size 10.6

  $slide5 = $presentation.Slides.Item(5)
  Set-Text -Shape $slide5.Shapes.Item(3) -Text "Phase C/D:`rPhysical Solve and Buyer Settlement"
  $table5 = $slide5.Shapes.Item(1).Table
  $physicalRows = @(
    @("Scenario", "Bounded-optimization lane with mandatory non-zero PV and BESS"),
    @("Load Basis", "184,262,276 kWh/yr industrial proxy from saigon18 inputs"),
    @("Market Basis", "CFMP/FMP and TOU tariff reconstructed from same-site workstream"),
    @("Sizing Result", "PV 4,800 kW; BESS 1,500 kW / 3,300 kWh; all at active upper bounds"),
    @("Settlement Math", "Matched = 6.84 GWh; shortfall = 177.42 GWh; shortfall settles at EVN retail"),
    @("Buyer Outcome", "353.9B VND/yr total payment vs 351.0B VND/yr EVN benchmark: FAIL")
  )
  for ($r = 1; $r -le $physicalRows.Count; $r++) {
    Set-TableCell -Table $table5 -Row $r -Column 1 -Text $physicalRows[$r - 1][0] -Size 10.5 -Bold -1 -Color $ink
    Set-TableCell -Table $table5 -Row $r -Column 2 -Text $physicalRows[$r - 1][1] -Size 10.3 -Bold 0 -Color $ink
  }
  Add-PlainRect -Slide $slide5 -Left 470 -Top 80 -Width 225 -Height 312 -FillColor $white | Out-Null
  Add-RoundedPanel -Slide $slide5 -Left 484 -Top 96 -Width 196 -Height 36 -FillColor $greenMid | Out-Null
  Add-TextBox -Slide $slide5 -Left 498 -Top 103 -Width 170 -Height 20 -Text "Settlement Snapshot" -Size 16 -Bold -1 -Color $white | Out-Null
  Add-RoundedPanel -Slide $slide5 -Left 492 -Top 150 -Width 180 -Height 52 -FillColor $greenTint | Out-Null
  Add-TextBox -Slide $slide5 -Left 504 -Top 160 -Width 156 -Height 32 -Text "6.84 GWh matched" -Size 18 -Bold -1 -Color $greenDark | Out-Null
  Add-RoundedPanel -Slide $slide5 -Left 492 -Top 214 -Width 180 -Height 52 -FillColor $greenTint | Out-Null
  Add-TextBox -Slide $slide5 -Left 500 -Top 224 -Width 162 -Height 32 -Text "177.42 GWh shortfall" -Size 17 -Bold -1 -Color $greenDark | Out-Null
  Add-RoundedPanel -Slide $slide5 -Left 492 -Top 278 -Width 180 -Height 60 -FillColor $greenSoft | Out-Null
  Add-TextBox -Slide $slide5 -Left 500 -Top 288 -Width 164 -Height 42 -Text "Blended buyer cost 1,920.76 VND/kWh" -Size 14 -Bold -1 -Color $ink | Out-Null
  Add-TextBox -Slide $slide5 -Left 495 -Top 350 -Width 174 -Height 30 -Text "The physical optimum does not create a commercial optimum." -Size 12 -Bold -1 -Color $gray | Out-Null

  $slide6 = $presentation.Slides.Item(6)
  Set-Text -Shape $slide6.Shapes.Item(1) -Text "Combined Economics Summary"
  Set-Text -Shape $slide6.Shapes.Item(2) -Text "At the 5%-below-EVN strike, the case fails both gates: buyer cost rises above EVN and developer revenue cannot service debt."
  $stats = $slide6.Shapes.Item(3).GroupItems
  Set-Text -Shape $stats.Item(2) -Text "Buyer delta"
  Set-Text -Shape $stats.Item(3) -Text "+2.9B"
  Set-Text -Shape $stats.Item(5) -Text "Matched share"
  Set-Text -Shape $stats.Item(6) -Text "3.7%"
  Set-Text -Shape $stats.Item(8) -Text "Min DSCR"
  Set-Text -Shape $stats.Item(9) -Text "-0.175"
  Set-Text -Shape $stats.Item(11) -Text "After-tax NPV"
  Set-Text -Shape $stats.Item(12) -Text "-`$6.05M"
  Add-PlainRect -Slide $slide6 -Left 414 -Top 109 -Width 279 -Height 139 -FillColor $white | Out-Null
  Add-RoundedPanel -Slide $slide6 -Left 430 -Top 122 -Width 250 -Height 30 -FillColor $greenMid | Out-Null
  Add-TextBox -Slide $slide6 -Left 440 -Top 128 -Width 230 -Height 18 -Text "Revenue vs debt service" -Size 14 -Bold -1 -Color $white | Out-Null
  Add-RoundedPanel -Slide $slide6 -Left 438 -Top 166 -Width 92 -Height 56 -FillColor $greenTint | Out-Null
  Add-TextBox -Slide $slide6 -Left 450 -Top 178 -Width 68 -Height 30 -Text "`$474K`rRevenue" -Size 15 -Bold -1 -Color $greenDark | Out-Null
  Add-RoundedPanel -Slide $slide6 -Left 560 -Top 154 -Width 98 -Height 68 -FillColor (OleColor 242 220 219) | Out-Null
  Add-TextBox -Slide $slide6 -Left 571 -Top 170 -Width 78 -Height 34 -Text "`$810K`rDebt svc" -Size 15 -Bold -1 -Color $failRed | Out-Null
  Add-TextBox -Slide $slide6 -Left 441 -Top 229 -Width 220 -Height 14 -Text "Revenue covers only ~59% of annual debt service before O&M." -Size 10.5 -Bold -1 -Color $gray | Out-Null
  Add-PlainRect -Slide $slide6 -Left 26 -Top 211 -Width 341 -Height 168 -FillColor $white | Out-Null
  Add-TableTitle -Slide $slide6 -Left 26 -Top 211 -Width 341 -Height 16 -Text "Buyer settlement" | Out-Null
  $tblBuyer = $slide6.Shapes.AddTable(5, 2, 26, 227, 341, 152).Table
  $buyerRows = @(
    @("Metric", "Value"),
    @("Buyer total payment", "353.9B VND/yr"),
    @("EVN benchmark", "351.0B VND/yr"),
    @("Blended DPPA cost", "1,920.76 VND/kWh"),
    @("Outcome", "FAIL: cost premium remains")
  )
  for ($r = 1; $r -le $buyerRows.Count; $r++) {
    for ($c = 1; $c -le 2; $c++) {
      $header = $r -eq 1
      Set-TableCell -Table $tblBuyer -Row $r -Column $c -Text $buyerRows[$r - 1][$c - 1] -Size ($(if ($header) { 10.2 } else { 9.6 })) -Bold ($(if ($header -or $c -eq 1) { -1 } else { 0 })) -Color ($(if ($header) { $white } else { $ink }))
      if ($header) { $tblBuyer.Cell($r,$c).Shape.Fill.ForeColor.RGB = $greenDark }
    }
  }
  Add-PlainRect -Slide $slide6 -Left 401 -Top 265 -Width 307 -Height 114 -FillColor $white | Out-Null
  Add-TableTitle -Slide $slide6 -Left 401 -Top 265 -Width 307 -Height 16 -Text "Developer screen" | Out-Null
  $tblDev = $slide6.Shapes.AddTable(5, 2, 401, 281, 307, 98).Table
  $devRows = @(
    @("Metric", "Value"),
    @("All-in PPA rate", "2,334.46 VND/kWh"),
    @("Year-1 revenue", "~`$474K"),
    @("Debt service", "~`$810K/yr"),
    @("Needed rate", "~3,900+ VND/kWh")
  )
  for ($r = 1; $r -le $devRows.Count; $r++) {
    for ($c = 1; $c -le 2; $c++) {
      $header = $r -eq 1
      Set-TableCell -Table $tblDev -Row $r -Column $c -Text $devRows[$r - 1][$c - 1] -Size ($(if ($header) { 9.6 } else { 9.2 })) -Bold ($(if ($header -or $c -eq 1) { -1 } else { 0 })) -Color ($(if ($header) { $white } else { $ink }))
      if ($header) { $tblDev.Cell($r,$c).Shape.Fill.ForeColor.RGB = $navy }
    }
  }

  $slide7 = $presentation.Slides.Item(7)
  Set-Text -Shape $slide7.Shapes.Item(1) -Text "Methodology:`rFive-Phase Decision Workflow"
  Set-Text -Shape $slide7.Shapes.Item(3) -Text "Case 3 was built as a realism-first bridge workflow.`r`rContext: same-site saigon18 load, CFMP/FMP, and tariff inputs were frozen before optimization to avoid the cross-site mismatch that broke Case 2.`r`rWorkflow used:`rPhase C physical solve with a storage floor -> Phase D buyer settlement under EVN benchmark -> Phase E controller-vs-optimizer dispatch gap -> Phase F PySAM developer finance gate -> Phase G combined recommendation.`r`rDecision rule: advance only if buyer beats EVN benchmark AND developer clears NPV > 0 and DSCR >= 1.0."
  Add-PlainRect -Slide $slide7 -Left 18.5 -Top 82 -Width 230 -Height 307 -FillColor $white | Out-Null
  $y = 94
  foreach ($step in @(
    "C  Physical solve",
    "D  Buyer settlement",
    "E  Dispatch gap",
    "F  Developer screen",
    "G  Combined decision"
  )) {
    Add-RoundedPanel -Slide $slide7 -Left 36 -Top $y -Width 194 -Height 38 -FillColor $greenTint | Out-Null
    Add-TextBox -Slide $slide7 -Left 48 -Top ($y + 8) -Width 170 -Height 22 -Text $step -Size 16 -Bold -1 -Color $greenDark | Out-Null
    $y += 50
  }

  $slide8 = $presentation.Slides.Item(8)
  Set-Text -Shape $slide8.Shapes.Item(1) -Text "Dispatch Gap:`rController Logic vs REopt Free Dispatch"
  Set-Text -Shape $slide8.Shapes.Item(2) -Text "Phase E exposed a structural mismatch between settlement math and optimizer behavior.`r`rContext: the controller proxy forces charge/discharge windows and shows 1,430 kWh of matched BESS discharge at the base sizing. The bounded-opt REopt dispatch at 4.8 MW PV / 1.5 MW BESS reports 0 kWh of matched BESS delivery because all battery behavior is absorbed as reduced EVN imports rather than explicit matched renewable output.`r`rImplication: when PV is tiny relative to site load, storage value appears inside import reduction, not as a separately visible matched-renewable stream. That weakens the commercial signal under the current DPPA settlement framing."
  Add-PlainRect -Slide $slide8 -Left 18.5 -Top 104.6 -Width 250.6 -Height 242.5 -FillColor $white | Out-Null
  Add-TableTitle -Slide $slide8 -Left 28 -Top 116 -Width 231 -Height 16 -Text "Controller vs optimizer" | Out-Null
  $tblGap = $slide8.Shapes.AddTable(4, 3, 28, 132, 231, 188).Table
  $gapRows = @(
    @("Metric", "Controller", "Optimizer"),
    @("Matched kWh", "1,430", "0"),
    @("Shortfall kWh", "184,253,166", "177,419,156"),
    @("Interpretation", "Visible BESS delivery", "Import reduction only")
  )
  for ($r = 1; $r -le $gapRows.Count; $r++) {
    for ($c = 1; $c -le 3; $c++) {
      $header = $r -eq 1
      Set-TableCell -Table $tblGap -Row $r -Column $c -Text $gapRows[$r - 1][$c - 1] -Size ($(if ($header) { 9.5 } else { 8.8 })) -Bold ($(if ($header -or $c -eq 1) { -1 } else { 0 })) -Color ($(if ($header) { $white } else { $ink }))
      if ($header) { $tblGap.Cell($r,$c).Shape.Fill.ForeColor.RGB = $greenDark }
    }
  }

  $slide9 = $presentation.Slides.Item(9)
  Set-Text -Shape $slide9.Shapes.Item(3) -Text "Why the Current Minimum Still Fails"
  Set-Text -Shape $slide9.Shapes.Item(1) -Text "The case is not failing because the model broke; it is failing because the constrained minimum is commercially too weak.`r`rFailure chain:`r1. Storage floor forces a non-zero BESS build.`r2. PV and BESS remain small relative to the 184.3 GWh site load.`r3. Most energy still clears through EVN imports at retail tariff.`r4. Buyer never sees enough cost relief to beat EVN.`r5. Developer never sees enough revenue to service debt at the buyer-constrained strike."
  Add-PlainRect -Slide $slide9 -Left 364.9 -Top 87 -Width 301.1 -Height 175.9 -FillColor $white | Out-Null
  Add-RoundedPanel -Slide $slide9 -Left 382 -Top 106 -Width 266 -Height 30 -FillColor $greenMid | Out-Null
  Add-TextBox -Slide $slide9 -Left 392 -Top 112 -Width 246 -Height 16 -Text "Commercial diagnosis" -Size 14 -Bold -1 -Color $white | Out-Null
  Add-TextBox -Slide $slide9 -Left 388 -Top 146 -Width 250 -Height 96 -Text "Buyer-side optimum does not equal bankable structure.`r`rThe case is constrained by low renewable penetration, not by lack of optimizer effort. A better answer requires a different strike, different sizing freedom, or better load data." -Size 12.5 -Bold 0 -Color $ink | Out-Null
  Set-Text -Shape $slide9.Shapes.Item(4) -Text "Implementation path:`rRun strike sensitivity from 0% to 20% below EVN. Remove or relax the storage floor and test smaller PV/BESS builds. Replace the static proxy with actual monthly bills and 8760 site load. Complete the 22kV branch and compare whether demand-charge economics materially change the recommendation."

  $slide10 = $presentation.Slides.Item(10)
  Set-Text -Shape $slide10.Shapes.Item(1) -Text "Recommended Actions:`rImmediate Next Pass"
  Set-Text -Shape $slide10.Shapes.Item(3) -Text "Recommended next pass:`r1. Reopen the strike anchor. The current 5%-below-EVN ceiling is too low for the developer and still not good enough for the buyer.`r2. Run a bounded strike sweep and estimate the lowest rate that clears both buyer and developer gates.`r3. Test smaller PV/BESS combinations and a no-storage-floor case to see whether the commercial minimum sits below the current build.`r4. Bring in actual project monthly bills and 8760 load to validate the 177 GWh shortfall signal.`r5. Complete the 22kV branch so the team can compare TOU and demand-charge economics before any commercial negotiation."

  $slide11 = $presentation.Slides.Item(11)
  Set-Text -Shape $slide11.Shapes.Item(1) -Text "Risks and Review Prompts:`rWhat Still Needs Validation"
  Set-Text -Shape $slide11.Shapes.Item(4) -Text "Open questions for the next review:`rHow different is the actual project load from the static proxy, and does that change matched renewable share materially?`rWould a 4-hour battery or a smaller PV/BESS build improve commercial alignment more than the current constrained minimum?`rDoes the 22kV two-part tariff create demand-charge relief that the TOU branch misses?`rHow high can strike move before the buyer rejects on principle rather than economics?"
  Set-Text -Shape $slide11.Shapes.Item(3) -Text "Decision for this stage:`rDo not advance the current Case 3 structure into negotiation or investment screening. Use it as a negative but useful bridge result that narrows the next modeling moves."

  $slide12 = $presentation.Slides.Item(12)
  Set-Text -Shape $slide12.Shapes.Item(5) -Text "Tung Ho, tah@allotropepartners.com`rDPPA Case 3 final decision deck`rAllotrope Partners Vietnam energy analysis"

  $presentation.Save()
  $presentation.Export($PreviewDir, "PNG")
}
finally {
  $presentation.Close()
  $ppt.Quit()
}

Write-Output $OutputPath
