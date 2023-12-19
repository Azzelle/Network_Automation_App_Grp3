from ncclient import manager
from ncclient.operations import TimeoutExpiredError
import xml.etree.ElementTree as ET
import requests
import json

DEVICE_IP = '192.168.194.128'
DEVICE_PORT = 830
DEVICE_USERNAME = 'cisco'
DEVICE_PASSWORD = 'cisco123!'
HOSTKEY_VERIFY = False


def connect_to_device():
    try:
        device = manager.connect(
            host=DEVICE_IP,
            port=DEVICE_PORT,
            username=DEVICE_USERNAME,
            password=DEVICE_PASSWORD,
            hostkey_verify=HOSTKEY_VERIFY,
            device_params={'name': 'default'},
            timeout=10,
        )
        return device
    
    except Exception as e:
        print(f"Failed to connect to the device: {e}")
        return None
    

def get_running_config(device):
    try:
        running_config = device.get_config(source='running').data_xml
        return running_config
    
    except TimeoutError:
        print("Timeout: Unable to retrieve running configuration.")
        return None


def make_running_changes(device):
    try:
        changes = """
                    <config>
                        <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
                            <enable>
                                <password>
                                    <secret>cisco123!</secret>
                                </password>
                            </enable>
                        </native>
                        <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                            <interface>
                                <name>GigabitEthernet1</name>
                                <description>Main interface for CSR1000v device</description>
                            </interface>
                            <interface>
                                <name>Loopback0</name>
                                <description>Loopback interface</description>
                                <type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:softwareLoopback</type>
                                <enabled>true</enabled>
                                <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
                                    <address>
                                        <ip>192.168.0.1</ip>
                                        <netmask>255.255.255.255</netmask>
                                    </address>
                                </ipv4>
                            </interface>
                        </interfaces>
                    </config>
                """
        device.edit_config(target='running', config=changes)
        print("Configuration changes applied.")

    except TimeoutExpiredError:
        print("Timeout: Unable to apply configuration changes.")


def send_notifications(access_token="", roomId="", message=""):
    """Send notifications to Webex Teams once the
    configuration has been updated."""

    # Payload to send to API
    payload = {
      "roomId": roomId,
      "text": message,
    }

    # Headers
    headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {access_token}"
    }

    # Sends request to the API
    response = requests.post("https://webexapis.com/v1/messages", headers=headers, json=payload)
    print(response.json())

def main():
    device = connect_to_device()
    
    if device:
        running_config_before = get_running_config(device)
        
        if running_config_before:
            make_running_changes(device)
            running_config_after = get_running_config(device)
            
            if running_config_after:

                if running_config_before != running_config_after:
                    send_notifications(
                        access_token="MTc3OTVlMmQtMTU2Zi00NWMzLWJlMGYtOTc1NmUwYTBkODUxZDgzYjAyOTctZWRm_P0A1_f5e58214-0ff5-4066-82da-b1a7c6c6a57a",
                        roomId="Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL1JPT00vNTA1YjZkOTAtOWU3Ny0xMWVlLWJlMzctODkzODU3YzE1Mjcw",
                        message="Network configuration has been updated.") # Add ID info from webex
                
                else:
                    send_notifications(
                        access_token="MTc3OTVlMmQtMTU2Zi00NWMzLWJlMGYtOTc1NmUwYTBkODUxZDgzYjAyOTctZWRm_P0A1_f5e58214-0ff5-4066-82da-b1a7c6c6a57a",
                        roomId="Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL1JPT00vNTA1YjZkOTAtOWU3Ny0xMWVlLWJlMzctODkzODU3YzE1Mjcw",
                        message="No changes detected on the configuration.")
            
            device.close_session()
        
        else:
            print("Unable to proceed without the initial running config.")
    
    else:
        print("Unable to connect to device.")

if __name__ == "__main__":
    main()