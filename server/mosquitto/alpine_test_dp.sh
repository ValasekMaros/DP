#! usr/bin/bash
read -p "Number of records: " N
read -p "Sleep time in seconds: " SLEEP
read -p "MQTT Topic: " Topic
read -p "ID number (00): " id
read -p "Temperature(HIGH): " TempH
read -p "Temperature(LOW): " TempL
read -p "Humidity(HIGH): " HumH
read -p "Humidity(LOW): " HumL
read -p "Pressure(HIGH): " PressH
read -p "Pressure(LOW): " PressL
read -p "Rain(HIGH): " RainH
read -p "Rain(LOW): " RainL
read -p "Wind Speed(HIGH): " WindSpeedH
read -p "Wind Speed(LOW): " WindSpeedL
read -p "Wind Direction(HIGH): " WindDirH
read -p "Wind Direction(LOW): " WindDirL
read -p "Battery Voltage(HIGH): " BattVolH
read -p "Battery Voltage(LOW): " BattVolL
DIFFT=$(($TempH-$TempL+1))
DIFFH=$(($HumH-$HumL+1))
DIFFP=$(($PressH-$PressL+1))
DIFFR=$(($RainH-$RainL+1))
DIFFWS=$(($WindSpeedH-$WindSpeedL+1))
DIFFWD=$(($WindDirH-$WindDirL+1))
DIFFBV=$(($BattVolH-$BattVolL+1))
RANDOM=$$
RANDOMSIX=$((RANDOM % 7 + 0))
echo ""
echo "Start Testing..."
echo ""

for i in $(seq $N)
do
        echo "Record Number: $i"
        TBME=$(($(($RANDOM%$DIFFT))+$TempL))
        TDHT=$(($(($RANDOM%$DIFFT))+$TempL))
        HBME=$(($(($RANDOM%$DIFFH))+$HumL))
        HDHT=$(($(($RANDOM%$DIFFH))+$HumL))
        P=$(($(($RANDOM%$DIFFP))+$PressL))
        R=$(($(($RANDOM%$DIFFR))+$RainL))
        WS=$(($(($RANDOM%$DIFFWS))+$WindSpeedL))
        WSKM=$((WS*3))
        WD=$(($(($RANDOM%$DIFFWD))+$WindDirL))
        BV=$(($(($RANDOM%$DIFFBV))+$BattVolL))

        case $RANDOMSIX in
                "0")
                        STATUS="OK"
                        ;;
                "1")
                        STATUS="Error:WiFi"
                        ;;
                "2")
                        STATUS="Error:BME/DHT"
                        ;;
                "3")
                        STATUS="Error:MS-WH-SP-RG"
                        ;;
                "4")
                        STATUS="Error:WH-SP-WS01"
                        ;;
                "5")
                        STATUS="Error:WH-SP-WD"
                        ;;
                "6")
                        STATUS="Error:MQTT"
                        ;;
        esac

        mosquitto_pub -u dp -P Valasek_Maros -t "$Topic" -m {'"espID"':'"'$id'"'", "'"bme_temp"':$TBME", "'"bme_hum"':$HBME", "'"bme_press"':$P", "'"dht_temp"':$TDHT", "'"dht_hum"':$HDHT", "'"rain_tips"':$RANDOM", "'"rain_mm"':$R", "'"windSpeed_tips"':$RANDOM", "'"windSpeed_1Hz"':$RANDOM", "'"windSpeed_kmh"':$WSKM", "'"windSpeed_ms"':$WS", "'"windDir_deg"':$WD", "'"windDir_Name"':'"'N'"'", "'"windDir_ADC"':$WD", "'"battery_voltage"':$BV", "'"status"':'"'$STATUS'"'}
        sleep $SLEEP
done

echo ""
echo "Test ended..."
echo ""
