KPI_CONFIG = {

    # ==========================================================
    # CPU
    # ==========================================================

    "CPU": [

        {
            "name": "CPU Utilization %",
            "execution_order": 1,
            "linux": "mpstat 1 1",
            "windows": r'''powershell -NoProfile -Command "(Get-Counter '\Processor(_Total)\% Processor Time' -MaxSamples 1).CounterSamples[0].CookedValue"''',
        },

        {
            "name": "User CPU %",
            "execution_order": 2,
            "linux": "mpstat 1 1",
            "windows": r'''powershell -NoProfile -Command "(Get-Counter '\Processor(_Total)\% User Time' -MaxSamples 1).CounterSamples[0].CookedValue"''',
        },

        {
            "name": "System CPU %",
            "execution_order": 3,
            "linux": "mpstat 1 1",
            "windows": r'''powershell -NoProfile -Command "(Get-Counter '\Processor(_Total)\% Privileged Time' -MaxSamples 1).CounterSamples[0].CookedValue"''',
        },

        {
            "name": "Load Average",
            "execution_order": 4,
            "linux": "cat /proc/loadavg",
            "windows": r'''powershell -NoProfile -Command "(Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average"''',
        },

        {
            "name": "Context Switch/sec",
            "execution_order": 5,
            "linux": "vmstat 1 2",
            "windows": r'''powershell -NoProfile -Command "(Get-Counter '\System\Context Switches/sec' -MaxSamples 1).CounterSamples[0].CookedValue"''',
        },

        {
            "name": "Interrupt/sec",
            "execution_order": 6,
            "linux": "vmstat -s",
            "windows": r'''powershell -NoProfile -Command "(Get-Counter '\Processor(_Total)\Interrupts/sec' -MaxSamples 1).CounterSamples[0].CookedValue"''',
        },

        {
            "name": "CPU Frequency",
            "execution_order": 7,
            "linux": "lscpu",
            "windows": r'''powershell -NoProfile -Command "(Get-CimInstance Win32_Processor | Select-Object -First 1 -ExpandProperty CurrentClockSpeed)"''',
        },

        # {
        #     "name": "CPU Temperature",
        #     "execution_order": 8,
        #     "linux": "sensors",
        #     "windows": r'''powershell -NoProfile -Command "$t=Get-CimInstance -Namespace root/WMI -ClassName MSAcpi_ThermalZoneTemperature -ErrorAction SilentlyContinue; if($t){[math]::Round((($t | Measure-Object CurrentTemperature -Average).Average / 10) - 273.15,2)}else{Write-Output 'N/A'}"''',
        # },

        {
            "name": "CPU Utilization by Core",
            "execution_order": 9,
            "linux": "mpstat -P ALL 1 1",
            "windows": r'''powershell -NoProfile -Command "$x=(Get-Counter '\Processor(*)\% Processor Time' -MaxSamples 1).CounterSamples | Where-Object {$_.InstanceName -ne '_Total'}; if(@($x).Count -gt 0){[math]::Round(($x | Measure-Object CookedValue -Average).Average,6)}else{exit 2}"''',
        },

    ],

    # ==========================================================
    # MEMORY
    # ==========================================================

    "MEMORY": [

        {
            "name": "Memory Usage %",
            "execution_order": 1,
            "linux": "free -m",
            "windows": r'''powershell -NoProfile -Command "(Get-Counter '\Memory\% Committed Bytes In Use' -MaxSamples 1).CounterSamples[0].CookedValue"''',
        },

        {
            "name": "Used/Free Memory",
            "execution_order": 2,
            "linux": "free -m",
            "windows": r'''powershell -NoProfile -Command "$m=Get-CimInstance Win32_OperatingSystem; $total=$m.TotalVisibleMemorySize/1024; $free=$m.FreePhysicalMemory/1024; [math]::Round($total-$free,2)"''',
        },

        {
            "name": "Swap Usage",
            "execution_order": 3,
            "linux": "free -m",
            "windows": r'''powershell -NoProfile -Command "(Get-Counter '\Paging File(_Total)\% Usage' -MaxSamples 1).CounterSamples[0].CookedValue"''',
        },

        {
            "name": "Page Fault/sec",
            "execution_order": 4,
            "linux": "vmstat 1 2",
            "windows": r'''powershell -NoProfile -Command "(Get-Counter '\Memory\Page Faults/sec' -MaxSamples 1).CounterSamples[0].CookedValue"''',
        },

        {
            "name": "Major Page Faults",
            "execution_order": 5,
            "linux": "sar -B 1 1",
            "windows": r'''powershell -NoProfile -Command "(Get-Counter '\Memory\Pages Input/sec' -MaxSamples 1).CounterSamples[0].CookedValue"''',
        },

    ],

    # ==========================================================
    # DISK
    # ==========================================================

    "DISK": [

        {
            "name": "Disk Usage %",
            "execution_order": 1,
            "linux": "df -P",
            "windows": r'''powershell -NoProfile -Command "$d=@(Get-CimInstance Win32_LogicalDisk -Filter 'DriveType=3' | Where-Object {$_.Size -gt 0}); $total=($d | Measure-Object Size -Sum).Sum; $free=($d | Measure-Object FreeSpace -Sum).Sum; if($total -gt 0){[math]::Round((($total-$free)/$total)*100,2)}else{exit 2}"''',
        },

        {
            "name": "Disk IOPS",
            "execution_order": 2,
            "linux": "iostat -dx 1 2",
            "windows": r'''powershell -NoProfile -Command "(Get-Counter '\PhysicalDisk(_Total)\Disk Transfers/sec' -MaxSamples 1).CounterSamples[0].CookedValue"''',
        },

        {
            "name": "Disk Latency",
            "execution_order": 3,
            "linux": "iostat -dx 1 2",
            "windows": r'''powershell -NoProfile -Command "(Get-Counter '\PhysicalDisk(_Total)\Avg. Disk sec/Transfer' -MaxSamples 1).CounterSamples[0].CookedValue"''',
        },

        {
            "name": "Disk Queue",
            "execution_order": 4,
            "linux": "iostat -x 1 2",
            "windows": r'''powershell -NoProfile -Command "(Get-Counter '\PhysicalDisk(_Total)\Current Disk Queue Length' -MaxSamples 1).CounterSamples[0].CookedValue"''',
        },

        {
            "name": "SMART Health",
            "execution_order": 5,
            "linux": "smartctl -H /dev/sda",
            "windows": r'''powershell -NoProfile -Command "$d=@(Get-PhysicalDisk -ErrorAction SilentlyContinue); if($d.Count -eq 0){exit 2}; $bad=@($d | Where-Object {$_.HealthStatus -ne 'Healthy'}); if($bad.Count -eq 0){1}else{0}"''',
        },

    ],

    # ==========================================================
    # NETWORK
    # ==========================================================

    "NETWORK": [

        {
            "name": "Bandwidth",
            "execution_order": 1,
            "linux": "sar -n DEV 1 2",
            "windows": r'''powershell -NoProfile -Command "$x=(Get-Counter '\Network Interface(*)\Bytes Total/sec' -MaxSamples 1).CounterSamples; if(@($x).Count -gt 0){[math]::Round(($x | Measure-Object CookedValue -Sum).Sum,2)}else{exit 2}"''',
        },

        {
            "name": "TCP Connections",
            "execution_order": 2,
            "linux": "ss -ant",
            "windows": r'''powershell -NoProfile -Command "@(Get-NetTCPConnection -ErrorAction SilentlyContinue).Count"''',
        },

        {
            "name": "UDP Connections",
            "execution_order": 3,
            "linux": "ss -anu",
            "windows": r'''powershell -NoProfile -Command "@(Get-NetUDPEndpoint -ErrorAction SilentlyContinue).Count"''',
        },

        {
            "name": "Packet Loss",
            "execution_order": 4,
            "linux": "ping -c 4 8.8.8.8",
            "windows": r'''powershell -NoProfile -Command "$r=@(Test-Connection 8.8.8.8 -Count 4 -ErrorAction SilentlyContinue); $received=$r.Count; [math]::Round(((4-$received)/4)*100,2)"''',
        },

        {
            "name": "DNS Resolution",
            "execution_order": 5,
            "linux": "dig google.com",
            "windows": r'''powershell -NoProfile -Command "try{$x=Resolve-DnsName google.com -Type A -ErrorAction Stop | Where-Object {$_.Type -eq 'A'} | Select-Object -First 1;if($null -ne $x){1}else{0}}catch{0}"''',
        },

    ],

    # ==========================================================
    # PROCESSES
    # ==========================================================

    "PROCESSES": [

        {
            "name": "Top Processes",
            "execution_order": 1,
            "linux": "ps aux --sort=-%cpu | head -n 11",
            "windows": r'''powershell -NoProfile -Command "@(Get-Process -ErrorAction SilentlyContinue | Sort-Object CPU -Descending | Select-Object -First 10).Count"''',
        },

        {
            "name": "Thread Count",
            "execution_order": 2,
            "linux": "ps -eLf",
            "windows": r'''powershell -NoProfile -Command "$x=@(Get-Process -ErrorAction SilentlyContinue | ForEach-Object {$_.Threads.Count}); [math]::Round(($x | Measure-Object -Sum).Sum,0)"''',
        },

        {
            "name": "Open Files",
            "execution_order": 3,
            "linux": "lsof",
            "windows": r'''powershell -NoProfile -Command "$x=@(Get-Process -ErrorAction SilentlyContinue | Where-Object {$null -ne $_.HandleCount}); [math]::Round(($x.HandleCount | Measure-Object -Sum).Sum,0)"''',
        },

    ],

    # ==========================================================
    # SERVICES
    # ==========================================================

    "SERVICES": [

        {
            "name": "Service Status",
            "execution_order": 1,
            "linux": "systemctl list-units --type=service --all --no-pager",
            "windows": r'''powershell -NoProfile -Command "@(Get-Service -ErrorAction SilentlyContinue).Count"''',
        },

        {
            "name": "Failed Services",
            "execution_order": 2,
            "linux": "systemctl --failed --type=service --no-pager",
            "windows": r'''powershell -NoProfile -Command "@(Get-Service -ErrorAction SilentlyContinue | Where-Object {$_.Status -ne 'Running'}).Count"''',
        },

        {
            "name": "Startup Type",
            "execution_order": 3,
            "linux": "systemctl list-unit-files --type=service --no-pager",
            "windows": r'''powershell -NoProfile -Command "@(Get-CimInstance Win32_Service -ErrorAction SilentlyContinue | Where-Object {$_.StartMode -eq 'Auto'}).Count"''',
        },

    ],

    # ==========================================================
    # OS
    # ==========================================================

    "OS": [

        {
            "name": "Uptime",
            "execution_order": 1,
            "linux": "uptime -p",
            "windows": r'''powershell -NoProfile -Command "$boot=(Get-CimInstance Win32_OperatingSystem).LastBootUpTime; [math]::Round(((Get-Date)-$boot).TotalSeconds,0)"''',
        },

        {
            "name": "Logged Users",
            "execution_order": 2,
            "linux": "who",
            "windows": r'''powershell -NoProfile -Command "@(quser 2>$null | Select-Object -Skip 1).Count"''',
        },

        {
            "name": "Pending Reboot",
            "execution_order": 4,
            "linux": None,
            "windows": r'''powershell -NoProfile -Command "$reboot=$false; $p1='HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing\RebootPending'; $p2='HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired'; $p3='HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager'; if(Test-Path $p1){$reboot=$true}; if(Test-Path $p2){$reboot=$true}; $x=Get-ItemProperty -Path $p3 -Name PendingFileRenameOperations -ErrorAction SilentlyContinue; if($null -ne $x.PendingFileRenameOperations){$reboot=$true}; if($reboot){1}else{0}"''',
        },

    ],

    # ==========================================================
    # TCP FIN WAIT
    # ==========================================================

    "TCP_FIN_WAIT": [

        {
            "name": "FIN_WAIT_1",
            "execution_order": 1,
            "linux": "ss -tan state fin-wait-1",
            "windows": r'''powershell -NoProfile -Command "@(Get-NetTCPConnection -State FinWait1 -ErrorAction SilentlyContinue).Count"''',
        },

        {
            "name": "FIN_WAIT_2",
            "execution_order": 2,
            "linux": "ss -tan state fin-wait-2",
            "windows": r'''powershell -NoProfile -Command "@(Get-NetTCPConnection -State FinWait2 -ErrorAction SilentlyContinue).Count"''',
        },

        {
            "name": "TIME_WAIT",
            "execution_order": 3,
            "linux": "ss -tan state time-wait",
            "windows": r'''powershell -NoProfile -Command "@(Get-NetTCPConnection -State TimeWait -ErrorAction SilentlyContinue).Count"''',
        },

        {
            "name": "CLOSE_WAIT",
            "execution_order": 4,
            "linux": "ss -tan state close-wait",
            "windows": r'''powershell -NoProfile -Command "@(Get-NetTCPConnection -State CloseWait -ErrorAction SilentlyContinue).Count"''',
        },

        {
            "name": "LAST_ACK",
            "execution_order": 5,
            "linux": "ss -tan state last-ack",
            "windows": r'''powershell -NoProfile -Command "@(Get-NetTCPConnection -State LastAck -ErrorAction SilentlyContinue).Count"''',
        },

    ],
}