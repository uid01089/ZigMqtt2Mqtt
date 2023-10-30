import logging
import time
import datetime
import json


import paho.mqtt.client as pahoMqtt
from PythonLib.Mqtt import Mqtt
from PythonLib.Scheduler import Scheduler
from PythonLib.DictUtil import DictUtil
from PythonLib.DateUtil import DateTimeUtilities

logger = logging.getLogger('ZigMqtt2Mqtt')


class ZigMqtt2Mqtt:

    def __init__(self, mqttClient: Mqtt, scheduler: Scheduler) -> None:

        self.mqttClient = mqttClient
        self.scheduler = scheduler

    def setup(self) -> None:

        self.mqttClient.subscribeIndependentTopic('tele/tasmota_FDB99A/SENSOR', self.receiveData)
        self.mqttClient.subscribeIndependentTopic('tele/tasmota_5741F9/SENSOR', self.receiveData)
        self.scheduler.scheduleEach(self.__keepAlive, 10000)

    def receiveData(self, payload: str) -> None:

        try:
            timeStamp = DateTimeUtilities.getCurrentDateString()

            receivedData = json.loads(payload)
            zbReceived = receivedData.get("ZbReceived")
            if zbReceived:
                for hexAddr, sensorData in zbReceived.items():
                    name = sensorData.get('Name', hexAddr)

                    data = DictUtil.flatDict(sensorData, name)

                    self.mqttClient.publishOnChange(name + "/Time", str(timeStamp))
                    for value in data:
                        self.mqttClient.publishOnChange(value[0], value[1])

        except Exception as e:
            logger.error("Exception occurs: " + str(e))

    def __keepAlive(self) -> None:
        self.mqttClient.publishIndependentTopic('/house/agents/ZigMqtt2Mqtt/heartbeat', DateTimeUtilities.getCurrentDateString())


def main() -> None:
    logging.basicConfig(level=logging.INFO)

    scheduler = Scheduler()

    mqttClient = Mqtt("koserver.iot", "/house/rooms", pahoMqtt.Client("ZigMqtt2Mqtt"))
    scheduler.scheduleEach(mqttClient.loop, 500)

    zigMqtt2Mqtt = ZigMqtt2Mqtt(mqttClient, scheduler)
    zigMqtt2Mqtt.setup()

    while (True):
        scheduler.loop()
        time.sleep(0.25)


if __name__ == '__main__':
    main()
