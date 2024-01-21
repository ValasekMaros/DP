#! usr/bin/bash
read -p "Number of records: " N
read -p "Sleep time in seconds: " SLEEP
read -p "ID number (00): " id
read -p "Temperature(HIGH): " TempH
read -p "Temperature(LOW): " TempL
read -p "Humidity(HIGH): " HumH
read -p "Humidity(LOW): " HumL
read -p "Pressure(HIGH): " PressH
read -p "Pressure(LOW): " PressL
DIFFT=$(($TempH-$TempL+1))
DIFFH=$(($HumH-$HumL+1))
DIFFB=$(($PressH-$PressL+1))
RANDOM=$$
echo ""
echo "Start Testing..."
echo ""

for((i=1;i<=$N;i++))
do
	echo "Number of record: $i"
	T=$(($(($RANDOM%$DIFFT))+$TempL))
	H=$(($(($RANDOM%$DIFFH))+$HumL))
	B=$(($(($RANDOM%$DIFFB))+$PressL))
	mosquitto_pub -h 192.168.1.250 -u dp -P Valasek_Maros -t "home/thp" -m {'"m"':'"'$id'"'", "'"t"':$T", "'"h"':$H", "'"b"':$B}
	sleep $SLEEP
done

echo ""
echo "Test ended..."
echo ""
