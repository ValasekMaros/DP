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
RANDOM1=$$
RANDOM2=$$
echo ""
echo "Start Testing..."
echo ""

for i in $(seq $N)
do
        echo "Record Number: $i"
        TBME=$(($(($RANDOM1%$DIFFT))+$TempL))
  	TDHT=$(($(($RANDOM2%$DIFFT))+$TempL))
        HBME=$(($(($RANDOM1%$DIFFH))+$HumL))
        HDHT=$(($(($RANDOM2%$DIFFH))+$HumL))
	P=$(($(($RANDOM1%$DIFFP))+$PressL))
  	R=$(($(($RANDOM1%$DIFFR))+$RainL))
  	WS=$(($(($RANDOM1%$DIFFWS))+$WindSpeedL))
  	WD=$(($(($RANDOM1%$DIFFWD))+$WindDirL))
  	BV=$(($(($RANDOM1%$DIFFBV))+$BattVolL))
        mosquitto_pub -u dp -P Valasek_Maros -t "$Topic" -m {'"espID"':'"'$id'"'", "'"bme_temp"':$T", "'"bme_hum"':$H", "'"bme_press"':$P", "'"dht_temp"':$T", "'"dht_hum"':$H", "'"rain_tips"':$Random1", "'"rain_mm"':$R", "'"windSpeed_tips"':$Random1", "'"windSpeed_1Hz"':$Random2", "'"windSpeed_kmh"':$Random1+$Random2/2", "'"windSpeed_ms"':$WS", "'"windDir_deg"':$WD", "'"windDir_Name"':"N"", "'"windDir_ADC"':$WD*100", "'"battery_voltage"':$BV}
        sleep $SLEEP
done

echo ""
echo "Test ended..."
echo ""
