import network
import time

# Replace with your network credentials
ssidList = ["", "", ""]
passwordList = ["", "", ""]

wlan = network.WLAN(network.STA_IF)

def scan_and_connect():
    wlan.active(True)
    wlan.disconnect()
    time.sleep(0.1)

    print("Scanning for Wi-Fi networks...")

    networks = wlan.scan()

    if len(networks) == 0:
        print("No networks found.")
        return

    maxRSSI = -1000
    bestNetworkIndex = -1

    for i, net in enumerate(networks):
        ssid = net[0].decode('utf-8')
        rssi = net[3]

        print("{}: {}, RSSI: {}".format(i + 1, ssid, rssi))

        for j in range(len(ssidList)):
            if ssid == ssidList[j] and rssi > maxRSSI:
                maxRSSI = rssi
                bestNetworkIndex = j

    if bestNetworkIndex == -1:
        print("No known networks found.")
    else:
        print("Connecting to the strongest network: {}".format(
            ssidList[bestNetworkIndex]
        ))

        wlan.connect(
            ssidList[bestNetworkIndex],
            passwordList[bestNetworkIndex]
        )

        while not wlan.isconnected():
            time.sleep(0.5)
            print(".", end="")

        if wlan.isconnected():
            print("\nConnected!")
            print("The ESP32-C3 is connected to Wi-Fi!")
            print("IP Address:", wlan.ifconfig()[0])
        else:
            print("The ESP32-C3 is NOT connected to Wi-Fi")

scan_and_connect()