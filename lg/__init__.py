import temescal
import json
from threading import Thread
import time

eg.RegisterPlugin(
    name = "LG SoundBar",
    author = "DanMabee",
    version = "1.0.0",
    kind = "external",
    guid = "{A15C1DA5-4966-4766-AD91-7C258D277528}",
    description = "A plugin for LG sound bars.",
)

class lg(eg.PluginBase):
    def __init__(self):
        self.values={}
        self.AddAction(PowerOn)
        self.AddAction(PowerOff)
        self.AddAction(MuteOn)
        self.AddAction(MuteOff)
        self.AddAction(MuteToggle)
        self.AddAction(SetVolume)
        self.AddAction(IncrementVolume)
        self.AddAction(SetFunction)
        self.AddAction(SetEqualizer)
        self.AddAction(GetFunction,hidden=True)
        self.AddAction(GetValues,hidden=True)
        self.AddAction(GetPower,hidden=True)
        self.AddAction(SendMessage)

    def Configure(self, address="", port=9741):
        panel = eg.ConfigPanel(self)
        addressText = panel.TextCtrl(address)
        portText = panel.TextCtrl(str(port))
        panel.AddLine("Address:", addressText)
        panel.AddLine("Port:", portText)
        while panel.Affirmed():
            panel.SetResult(
                addressText.GetValue(),
                int(portText.GetValue())
            )

    def __start__(self, address="", port=9741):
        self.address=address
        self.port=port
        self.lastTime=time.time()
        self.ts=temescal.temescal(self.address,self.port,self.listener)
        self.getall()
        self.monitorThread = Thread(target=self.monitor)
        self.monitorThread.start()

    def getall(self):
        self.ts.get_func()
        self.ts.get_eq()
        self.ts.get_info()
        self.ts.get_settings()
        self.ts.get_play()
        self.ts.get_product_info()
        self.ts.get_c4a_info()
        self.ts.get_update_info()
        self.ts.get_radio_info()
        self.ts.get_ap_info()
        self.ts.get_build_info()
        self.ts.get_option_info()
        self.ts.get_mac_info()
        self.ts.get_mem_mon_info()
        self.ts.get_test_info()

    def listener(self, response):
        self.lastTime=time.time()
        if response['result'] != 'sorry not support':
            if not response['msg'] in self.values:
                self.values[response['msg']]={}
            for key in response['data']:
                if not key in self.values[response['msg']] or self.values[response['msg']][key]!=response['data'][key]:
                    if key in self.values[response['msg']]:
                        self.TriggerEvent(response['msg']+"."+key,response['data'][key])
                        if response['msg']=='SPK_LIST_VIEW_INFO' and key=='b_powerstatus':
                            if response['data'][key] == True:
                                self.TriggerEvent("PowerOn")
                            else:
                                self.TriggerEvent("PowerOff")
                    self.values[response['msg']][key]=response['data'][key]

    def monitor(self):
        while True:
            time.sleep(60)
            try:
                self.ts.get_eq()
                if time.time()>self.lastTime+120:
                    print('new ts')
                    try:
                        self.ts.stop()
                    except:
                        pass
                    self.ts=temescal.temescal(self.address,self.port,self.listener)
                    self.getall()
            except:
                pass

    def increment_volume(self, value):
        self.ts.set_volume(value+self.values["SPK_LIST_VIEW_INFO"]["i_vol"])

class IncrementVolume(eg.ActionWithStringParameter):
    name = 'Alter Volume'

    def __call__(self, data):
        self.plugin.increment_volume(int(data))

class SetVolume(eg.ActionWithStringParameter):
    name = 'Set Volume'

    def __call__(self, data):
        self.plugin.ts.set_volume(int(data))

class PowerOn(eg.ActionBase):
    name = 'Power On'

    def __call__(self):
        self.plugin.ts.set_power(True)

class PowerOff(eg.ActionBase):
    name = 'Power Off'

    def __call__(self):
        self.plugin.ts.set_power(False)

class MuteOn(eg.ActionBase):
    name = 'Mute On'

    def __call__(self):
        self.plugin.ts.set_mute(True)

class MuteOff(eg.ActionBase):
    name = 'Mute Off'

    def __call__(self):
        self.plugin.ts.set_mute(False)

class MuteToggle(eg.ActionBase):
    name = 'Mute Toggle'

    def __call__(self):
        self.plugin.ts.set_mute(not self.plugin.values["SPK_LIST_VIEW_INFO"]["b_mute"])

class SetFunction(eg.ActionBase):
    name = 'Set Input'

    def __call__(self, parameter):
        self.plugin.ts.set_func(temescal.functions.index(parameter))

    def Configure(self, parameter=""):
        panel = eg.ConfigPanel(resizable=True)
        funclist=[]
        for val in self.plugin.values["FUNC_VIEW_INFO"]["ai_func_list"]:
            funclist.append(temescal.functions[val])
        if parameter=="":
            parameter=funclist[0]
        labelCtrl = panel.StaticText("Select Input:")
        panel.sizer.Add(labelCtrl, 0, wx.EXPAND)
        panel.sizer.Add((5, 5))
        parameterCtrl = panel.Choice(temescal.functions.index(parameter),funclist)
        panel.sizer.Add(parameterCtrl, 0, wx.EXPAND)
        parameterCtrl.SetFocus()
        while panel.Affirmed():
            panel.SetResult(funclist[parameterCtrl.GetValue()])

class GetFunction(eg.ActionBase):
    name = 'Get Input'

    def __call__(self):
        return temescal.functions[self.plugin.values["FUNC_VIEW_INFO"]["i_curr_func"]]

class GetPower(eg.ActionBase):
    name = 'Get power state'

    def __call__(self):
        return temescal.functions[self.plugin.values["SPK_LIST_VIEW_INFO"]["b_powerstatus"]]

class GetValues(eg.ActionBase):
    name = 'Get all values'

    def __call__(self):
        return self.plugin.values

class SetEqualizer(eg.ActionBase):
    name = 'Set Equalizer'

    def __call__(self, parameter):
        self.plugin.ts.set_eq(temescal.equalisers.index(parameter))

    def Configure(self, parameter=temescal.equalisers[0]):
        panel = eg.ConfigPanel(resizable=True)
        eqlist=[]
        for val in self.plugin.values["EQ_VIEW_INFO"]["ai_eq_list"]:
            try:
                eqlist.append(temescal.equalisers[val])
            except:
                pass
        if parameter=="":
            parameter=eqlist[0]
        labelCtrl = panel.StaticText("Select Equalizer:")
        panel.sizer.Add(labelCtrl, 0, wx.EXPAND)
        panel.sizer.Add((5, 5))
        parameterCtrl = panel.Choice(temescal.equalisers.index(parameter),eqlist)
        panel.sizer.Add(parameterCtrl, 0, wx.EXPAND)
        parameterCtrl.SetFocus()
        while panel.Affirmed():
            panel.SetResult(eqlist[parameterCtrl.GetValue()])

class SendMessage(eg.ActionWithStringParameter):
    name = 'Send arbitrary message'

    def __call__(self, data):
        self.plugin.ts.send_packet(json.loads(data))
