import logging
import time
import json


import paho.mqtt.client as pahoMqtt
from PythonLib.JsonUtil import JsonUtil
from PythonLib.Mqtt import MQTTHandler, Mqtt
from PythonLib.Scheduler import Scheduler
from PythonLib.DictUtil import DictUtil
from PythonLib.DateUtil import DateTimeUtilities

logger = logging.getLogger('ZigMqtt2Mqtt')


class Module:
    def __init__(self) -> None:
        self.scheduler = Scheduler()
        self.mqttClient = Mqtt("koserver.iot", "/house/rooms", pahoMqtt.Client("ZigMqtt2Mqtt"))

    def getScheduler(self) -> Scheduler:
        return self.scheduler

    def getMqttClient(self) -> Mqtt:
        return self.mqttClient

    def setup(self) -> None:
        self.scheduler.scheduleEach(self.mqttClient.loop, 500)

    def loop(self) -> None:
        self.scheduler.loop()


class ZigMqtt2Mqtt:

    def __init__(self, module: Module) -> None:

        self.mqttClient = module.getMqttClient()
        self.scheduler = module.getScheduler()

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

        except BaseException:
            logging.exception('_1_')

    def __keepAlive(self) -> None:
        self.mqttClient.publishIndependentTopic('/house/agents/ZigMqtt2Mqtt/heartbeat', DateTimeUtilities.getCurrentDateString())
        self.mqttClient.publishIndependentTopic('/house/agents/ZigMqtt2Mqtt/subscriptions', JsonUtil.obj2Json(self.mqttClient.getSubscriptionCatalog()))


def main() -> None:
    logging.basicConfig(level=logging.INFO)

    module = Module()
    module.setup()

    logging.getLogger('ZigMqtt2Mqtt').addHandler(MQTTHandler(module.getMqttClient(), '/house/agents/ZigMqtt2Mqtt/log'))

    ZigMqtt2Mqtt(module).setup()

    print("ZigMqtt2Mqtt is running")

    while (True):
        module.loop()
        time.sleep(0.25)


if __name__ == '__main__':
    main()
