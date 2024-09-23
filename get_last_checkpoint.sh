if [ $2 = "local" ]; then
    last=$(ssh apirrone@192.168.1.221 "cd /home/apirrone/MISC/AMP_for_hardware/logs/bdx_amp/*_$1/ ; ls *.pt -lt | head -n 1" | awk '{print $8}')
else
    last=$(ssh -p4242 apirrone@s-nguyen.net "cd /home/apirrone/MISC/AMP_for_hardware/logs/bdx_amp/*_$1/ ; ls *.pt -lt | head -n 1" | awk '{print $8}')
fi

last_local=$(cd logs/bdx_amp/aze/ && ls *.pt -lt | head -n 1 | awk '{print $9}' && cd ../../..)

if [ "$last" == "$last_local" ]; then
    echo "No new file to download"
    exit 0
fi

if [ $2 = "local" ]; then
    scp apirrone@192.168.1.221:/home/apirrone/MISC/AMP_for_hardware/logs/bdx_amp/*_$1/$last logs/bdx_amp/aze/
else
    scp -p4242 apirrone@s-nguyen.net:/home/apirrone/MISC/AMP_for_hardware/logs/bdx_amp/*_$1/$last logs/bdx_amp/aze/
fi
