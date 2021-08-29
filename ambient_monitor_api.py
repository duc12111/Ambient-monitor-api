import time

from ambient_monitor import ComInterfaceAmbientMonitor
from typing import Union



class Ambient_monitor_api:
    """
    API  to the ComInterfaceAmbientMonitor
    """
    def __init__(self,timeout: float = 0.5):
        self._consumer=ComInterfaceAmbientMonitor(timeout)
        self._time_sleep=0.01
        
    @property
    def time_sleep(self)-> float:
        return self._time_sleep
    
    @time_sleep.setter
    def time_sleep(self, time_sleep:float):
        if (time_sleep==0):
            assert False, "time_sleep must >0"
        elif(self.timeout()!=None and time_sleep>self.timeout()):
            assert False, "time_sleep must < time out"
        else: self._time_sleep=time_sleep
        
    def timeout(self) -> Union[float, None]:
        """
        Get current ComInterfaceAmbientMonitor timeout setting.
        Return Union[float, None]
        """
            
        return self._consumer.timeout
    
    def set_timeout(self, new_timeout: Union[float, None]):
        """Set ComInterfaceAmbientMonitor timeout.
        
            @para new_timeout:Union[float, None]"""
        if(new_timeout!= None and self.time_sleep>=new_timeout):
            assert False, "timeout must > time_sleep"
        self._consumer.timeout(new_timeout)
        
    def _flush_data(self):
        """
        flush old data in CominterfaceAmbientMonitor """
        
        if(self._consumer.in_waiting!=0):
            self._consumer.read()
        
    def _wait_respond(self):
        """
        waiting respond from ComInterfaceAmbientMonitor """
        
        start=time.time()
        while(self._consumer.in_waiting==0 and time.time()-start<self.timeout()):
            time.sleep(self._time_sleep)
        
    def get_temperature(self)->float:
        """
        Get temperature from ambient monitor.
        
        Returns float 
        -------
        When receive too few or too many replies or not corrected reply then assert error.  """
        
        self._flush_data()
        self._consumer.write(':GET:TEMPERATURE:!'.encode('UTF-8'))
        self._wait_respond()
        reply =self._consumer.read(self._consumer.in_waiting).decode('UTF-8').split(":")
        #correct reply
        if len(reply)==5 and reply[1]=="REP" and reply[2]=="TEMPERATURE" and reply[4]=="!":
            return float(reply[3])
        
        else: self.error_handle(reply)
        
    def get_temperature_extremes(self)-> [float]:
        """
        Get temperature extremes from ambient monitor.
        
        Returns float 
        -------
        When receive too few or too many replies or not corrected reply then assert error.  """

        self._flush_data()
        self._consumer.write(':GET:TEMPERATURE_EXTREMES:!'.encode('UTF-8'))
        self._wait_respond()
        reply =self._consumer.read(self._consumer.in_waiting).decode('UTF-8').split(":")
        #correct reply
        if len(reply)==6 and reply[1]=="REP" and reply[2]=="TEMPERATURE_EXTREMES" and reply[5]=="!":
            return [float(reply[3]),float(reply[4])]
        
        else: self.error_handle(reply)
        
    def get_humidity(self)->int:
        """ 
        Get humidity from ambient monitor.
        
        Returns float 
        -------
        When receive too few or too many replies or not corrected reply then assert error.  """

        self._flush_data()        
        self._consumer.write(':GET:HUMIDITY:!'.encode('UTF-8'))
        self._wait_respond()
        reply =self._consumer.read(self._consumer.in_waiting).decode('UTF-8').split(":")
        #correct reply
        if len(reply)==5 and reply[1]=="REP" and reply[2]=="HUMIDITY" and reply[4]=="!":
            return int(reply[3])
        
        else: self.error_handle(reply)
        
    def get_humidity_extremes(self)->[int]:
         """
        Get temperature extremes from ambient monitor.
        
        Returns float 
        -------
        When receive too few or too many replies or not corrected reply then assert error. """

         self._flush_data()
         self._consumer.write(':GET:HUMIDITY_EXTREMES:!'.encode('UTF-8'))
         self._wait_respond()
         reply =self._consumer.read(self._consumer.in_waiting).decode('UTF-8').split(":")
         #correct reply
         if len(reply)==6 and reply[1]=="REP" and reply[2]=="HUMIDITY_EXTREMES" and reply[5]=="!":
             return [int(reply[3]),int(reply[4])]
         else: self.error_handle(reply)
         
    def set_reset_temperature(self):
        """
        Reset temperature
        -------
        assert error if not sucessful.  """
        
        self._flush_data()
        self._consumer.write(':SET:TEMPERATURE_RESET:!'.encode('UTF-8'))
        self._wait_respond()
        reply =self._consumer.read(self._consumer.in_waiting).decode('UTF-8')
        #correct reply
        if len(reply)==0 or ":REP:TEMPERATURE_RESET:!" not in reply:
             self.error_handle(reply.split(":"))
                     
    def set_reset_humidity(self):
        """
        Reset temperature
        -------
        assert error if not sucessful.  """
        
        self._flush_data()
        self._consumer.write(':SET:HUMIDITY_RESET:!'.encode('UTF-8'))
        self._wait_respond()
        reply =self._consumer.read(self._consumer.in_waiting).decode('UTF-8')
        #correct reply
        if len(reply)==0 or  ":REP:HUMIDITY_RESET:!" not in reply:
             self.error_handle(reply.split(":"))
           
    def error_handle(self,reply:[str]):
        """
        Error handling

        Parameters
        ----------
        reply : [str]  from read method of ComInterfaceAmbientMonitor then split by ':'
    
        -------
        assert error with all the error that meet

        """
        errors=[str]
        for i in range(len(reply)):
            if(reply[i]=="ERROR" and len(reply)>i+1):
                errors.append("ERROR: "+reply[i+1])  
        if(len(errors)==0):
            errors.append("Function did not run correctly")
        msg='\n'.join(str(error) for error in errors)
        assert False,msg   
        
if __name__ == "__main__":
    interface=Ambient_monitor_api()
    interface.time_sleep=0.01
    for i in range(100):
        if(i %6==0):
            print("get temperature: "+str(interface.get_temperature()))
        elif(i %6==1):
            print("get humidity: "+str(interface.get_humidity()))
        elif(i%6==2):
            print("get temperature extremes : " +str(interface.get_temperature_extremes()))
        elif(i%6==3):
            print("get humidity extremes : "+str(interface.get_humidity_extremes()))
        elif(i%6==4):
            interface.set_reset_temperature()
            #there might be a simulation update  between 2 commands
            print("set reset temperature : "+str(interface.get_temperature_extremes()))
        elif(i%6==5) :
            interface.set_reset_humidity()
            #there might be a simulation update  between 2 commands
            print("set reset humidity : "+ str(interface.get_humidity_extremes()))
        
        
