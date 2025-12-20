# Script fusion automatique des 17 PR
param([string]$targetBranch = "main")

Write-Host "====== Préparation ======" -ForegroundColor Green
git checkout $targetBranch
git pull origin $targetBranch

Write-Host "`nRécupération des PR..." -ForegroundColor Cyan
$prs = gh pr list --state open --json headRefName | ConvertFrom-Json

if ($prs.Count -eq 0) {
    Write-Host "Aucune PR trouvée." -ForegroundColor Yellow
    exit
}

Write-Host "Trouvé $($prs.Count) PR(s)" -ForegroundColor Green

$success = 0
$conflict = 0

foreach ($pr in $prs) {
    $branch = $pr.headRefName
    Write-Host "`n>>> Fusion de: $branch" -ForegroundColor Cyan
    
    git fetch origin $branch 2>$null
    git merge "origin/$branch" --no-commit --no-ff 2>$null
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "!!! CONFLIT: $branch !!!" -ForegroundColor Red
        Write-Host "Résolvez, puis:" -ForegroundColor Yellow
        Write-Host "  git add ." -ForegroundColor Yellow
        Write-Host "  git commit -m 'Fix: $branch'" -ForegroundColor Yellow
        Write-Host "  .\mass_merge.ps1" -ForegroundColor Yellow
        $conflict++
        break
    } else {
        git commit -m "Merge: $branch"
        Write-Host "? $branch OK" -ForegroundColor Green
        $success++
    }
}

Write-Host "`n====== RÉSUMÉ ======" -ForegroundColor Magenta
Write-Host "$success fusionnées, $conflict conflit(s)" -ForegroundColor Magenta
Write-Host "=====================" -ForegroundColor Magenta

if ($conflict -eq 0 -and $success -gt 0) {
    Write-Host "`nPush:" -ForegroundColor Green
    Write-Host "  git push origin main" -ForegroundColor Green
}
