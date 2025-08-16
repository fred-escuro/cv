# Batch CV Processor PowerShell Runner
# This PowerShell script provides an advanced interface for running the batch processor
# Supports .env configuration with command line overrides

param(
    [Parameter(Mandatory=$false)]
    [string]$FolderPath,
    
    [Parameter(Mandatory=$false)]
    [string]$FileTypes,
    
    [Parameter(Mandatory=$false)]
    [int]$Limit,
    
    [Parameter(Mandatory=$false)]
    [string]$LogFile,
    
    [Parameter(Mandatory=$false)]
    [string]$ErrorLogFile,
    
    [Parameter(Mandatory=$false)]
    [switch]$Verbose,
    
    [Parameter(Mandatory=$false)]
    [switch]$DryRun,
    
    [Parameter(Mandatory=$false)]
    [switch]$ShowConfig,
    
    [Parameter(Mandatory=$false)]
    [switch]$CreateEnv,
    
    [Parameter(Mandatory=$false)]
    [switch]$UseEnvConfig
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Function to display colored output
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

# Function to check prerequisites
function Test-Prerequisites {
    Write-ColorOutput "🔍 Checking prerequisites..." "Cyan"
    
    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ Python found: $pythonVersion" "Green"
        } else {
            throw "Python not available"
        }
    } catch {
        Write-ColorOutput "❌ Python is not installed or not in PATH" "Red"
        Write-ColorOutput "Please install Python 3.8+ and try again" "Yellow"
        return $false
    }
    
    # Check if script exists
    if (-not (Test-Path "batch_cv_processor.py")) {
        Write-ColorOutput "❌ batch_cv_processor.py not found" "Red"
        Write-ColorOutput "Please ensure you're running this from the batch_process directory" "Yellow"
        return $false
    }
    
    # Check if .env file exists
    if (Test-Path ".env") {
        Write-ColorOutput "✅ .env configuration file found" "Green"
    } else {
        Write-ColorOutput "⚠️  No .env file found. Using default configuration." "Yellow"
        Write-ColorOutput "   To create a .env file, run: python setup_config.py" "Cyan"
        Write-ColorOutput "   Or copy env_example.txt to .env and edit it." "Cyan"
    }
    
    # Check if folder exists (if specified)
    if ($FolderPath -and -not (Test-Path $FolderPath)) {
        Write-ColorOutput "❌ Folder does not exist: $FolderPath" "Red"
        return $false
    }
    
    Write-ColorOutput "✅ All prerequisites met" "Green"
    return $true
}

# Function to show configuration
function Show-Configuration {
    Write-ColorOutput "`n🔧 Current Configuration:" "Magenta"
    Write-ColorOutput "=" * 50 "Magenta"
    
    try {
        python batch_cv_processor.py --show-config
    } catch {
        Write-ColorOutput "❌ Could not display configuration: $($_.Exception.Message)" "Red"
    }
}

# Function to create .env template
function Create-EnvTemplate {
    Write-ColorOutput "`n📝 Creating .env template..." "Cyan"
    
    try {
        python batch_cv_processor.py --create-env
        Write-ColorOutput "✅ .env template created successfully!" "Green"
    } catch {
        Write-ColorOutput "❌ Could not create .env template: $($_.Exception.Message)" "Red"
    }
}

# Function to build command
function Build-Command {
    $command = @("python", "batch_cv_processor.py")
    
    # Add folder path if specified
    if ($FolderPath) {
        $command += $FolderPath
    }
    
    # Add other parameters
    if ($FileTypes) {
        $command += "--file-types", $FileTypes
    }
    
    if ($Limit) {
        $command += "--limit", $Limit.ToString()
    }
    
    if ($LogFile) {
        $command += "--log-file", $LogFile
    }
    
    if ($ErrorLogFile) {
        $command += "--error-log", $ErrorLogFile
    }
    
    return $command
}

# Function to display summary
function Show-Summary {
    Write-ColorOutput "`n📋 BATCH PROCESSING SUMMARY" "Magenta"
    Write-ColorOutput "=" * 50 "Magenta"
    
    if ($FolderPath) {
        Write-ColorOutput "📁 Folder: $FolderPath" "White"
    } else {
        Write-ColorOutput "📁 Folder: From .env configuration" "White"
    }
    
    if ($FileTypes) {
        Write-ColorOutput "🔍 File Types: $FileTypes" "White"
    } else {
        Write-ColorOutput "🔍 File Types: From .env configuration" "White"
    }
    
    if ($Limit) {
        Write-ColorOutput "📊 Limit: $Limit files" "White"
    } else {
        Write-ColorOutput "📊 Limit: From .env configuration" "White"
    }
    
    if ($LogFile) {
        Write-ColorOutput "📝 Log File: $LogFile" "White"
    } else {
        Write-ColorOutput "📝 Log File: From .env configuration" "White"
    }
    
    if ($ErrorLogFile) {
        Write-ColorOutput "❌ Error Log: $ErrorLogFile" "White"
    } else {
        Write-ColorOutput "❌ Error Log: From .env configuration" "White"
    }
    
    Write-ColorOutput "🔧 Dry Run: $($DryRun.IsPresent)" "White"
    Write-ColorOutput "🔧 Use .env: $($UseEnvConfig.IsPresent)" "White"
    Write-ColorOutput "=" * 50 "Magenta"
}

# Function to count files
function Get-FileCount {
    if (-not $FolderPath) {
        Write-ColorOutput "⚠️  No folder specified, cannot count files" "Yellow"
        return 0
    }
    
    try {
        $supportedExtensions = @('.pdf', '.doc', '.docx', '.rtf', '.txt', '.json', '.jpg', '.jpeg', '.png', '.bmp', '.tiff')
        
        if ($FileTypes) {
            $types = $FileTypes.Split(',') | ForEach-Object { ".$($_.Trim().ToLower())" }
        } else {
            $types = $supportedExtensions
        }
        
        $files = Get-ChildItem -Path $FolderPath -Recurse -File | Where-Object { $types -contains $_.Extension.ToLower() }
        return $files.Count
    } catch {
        Write-ColorOutput "⚠️ Could not count files: $($_.Exception.Message)" "Yellow"
        return 0
    }
}

# Function to show help
function Show-Help {
    Write-ColorOutput "`n🚀 Batch CV Processor PowerShell Runner" "Green"
    Write-ColorOutput "=" * 50 "Green"
    Write-ColorOutput "`nUsage Options:" "Cyan"
    Write-ColorOutput "1. Use .env configuration (default):" "White"
    Write-ColorOutput "   .\run_batch_processor.ps1" "Gray"
    Write-ColorOutput "   .\run_batch_processor.ps1 -UseEnvConfig" "Gray"
    Write-ColorOutput "`n2. Override with command line arguments:" "White"
    Write-ColorOutput "   .\run_batch_processor.ps1 -FolderPath 'C:\CVs' -Limit 100" "Gray"
    Write-ColorOutput "   .\run_batch_processor.ps1 -FolderPath 'C:\CVs' -FileTypes 'pdf,docx'" "Gray"
    Write-ColorOutput "`n3. Configuration management:" "White"
    Write-ColorOutput "   .\run_batch_processor.ps1 -ShowConfig" "Gray"
    Write-ColorOutput "   .\run_batch_processor.ps1 -CreateEnv" "Gray"
    Write-ColorOutput "`n4. Special modes:" "White"
    Write-ColorOutput "   .\run_batch_processor.ps1 -DryRun" "Gray"
    Write-ColorOutput "   .\run_batch_processor.ps1 -Verbose" "Gray"
    Write-ColorOutput "`n5. Combined usage:" "White"
    Write-ColorOutput "   .\run_batch_processor.ps1 -FolderPath 'C:\CVs' -Limit 50 -FileTypes 'pdf' -DryRun" "Gray"
    Write-ColorOutput "`nFor more options, run: python batch_cv_processor.py --help" "Yellow"
}

# Main execution
try {
    # Show help if no parameters
    if ($PSBoundParameters.Count -eq 0) {
        Show-Help
        exit 0
    }
    
    # Handle special commands first
    if ($ShowConfig.IsPresent) {
        if (-not (Test-Prerequisites)) { exit 1 }
        Show-Configuration
        exit 0
    }
    
    if ($CreateEnv.IsPresent) {
        if (-not (Test-Prerequisites)) { exit 1 }
        Create-EnvTemplate
        exit 0
    }
    
    # Check prerequisites
    if (-not (Test-Prerequisites)) {
        exit 1
    }
    
    # Show configuration if requested
    if ($UseEnvConfig.IsPresent) {
        Show-Configuration
    }
    
    # Count files if folder specified
    if ($FolderPath) {
        $fileCount = Get-FileCount
        if ($fileCount -gt 0) {
            Write-ColorOutput "📊 Found approximately $fileCount files to process" "Cyan"
        }
    }
    
    # Show summary
    Show-Summary
    
    # Confirm execution (unless dry run or showing config)
    if (-not $DryRun.IsPresent -and -not $ShowConfig.IsPresent -and -not $CreateEnv.IsPresent) {
        $confirmation = Read-Host "`nDo you want to proceed with processing? (y/N)"
        if ($confirmation -notmatch '^[Yy]') {
            Write-ColorOutput "❌ Processing cancelled by user" "Yellow"
            exit 0
        }
    }
    
    # Build and execute command
    $command = Build-Command
    
    Write-ColorOutput "`n🔄 Executing command..." "Cyan"
    Write-ColorOutput "Command: $($command -join ' ')" "Gray"
    
    if ($DryRun.IsPresent) {
        Write-ColorOutput "🔍 DRY RUN MODE - Command would execute:" "Yellow"
        Write-ColorOutput "$($command -join ' ')" "Gray"
        Write-ColorOutput "`n✅ Dry run completed. No files were processed." "Green"
    } else {
        Write-ColorOutput "`n🔄 Starting batch processing..." "Green"
        Write-ColorOutput "=" * 50 "Green"
        
        # Execute the command
        & $command[0] $command[1..($command.Length-1)]
        
        Write-ColorOutput "`n✅ Batch processing completed!" "Green"
        Write-ColorOutput "Check the output above for results and any log files generated." "Cyan"
    }
    
} catch {
    Write-ColorOutput "❌ Fatal error: $($_.Exception.Message)" "Red"
    if ($Verbose.IsPresent) {
        Write-ColorOutput "Stack trace:" "Red"
        $_.ScriptStackTrace
    }
    exit 1
}

Write-ColorOutput "`n🎉 Script execution completed successfully!" "Green"
