import lgpio

class Encoder:

    __KP = 0.0005
    __DT = 0.05
    

    def __init__(self, aPin : int, aChip ) -> None:
        self.__pin = aPin
        self.__chip = aChip
        self.__pulse_count = 0
        
        lgpio.gpio_claim_alert(self.__chip, self.__pin, lgpio.BOTH_EDGES, lgpio.SET_PULL_UP) # claim the GPIO pin for input lgpio.gpio_set_mode(chip, pin, lgpio.GPIO_MODE_INPUT) # set the pin as input lgpio.gpio_set_pull(chip, pin, lgpio.GPIO_PULL_UP) # enable pull-up resistor lgpio.gpio_set_alert_func(chip, pin, count_pulse_callback) # set the interrupt handler for this pin
        lgpio.callback(self.__chip, self.__pin, lgpio.BOTH_EDGES, func=self.__count_pulse_callback) # register the callback function for both rising and falling edges

    # chip = gpiochip, gpio = pin number, level = 0 or 1, tick = timestamp of event
    def __count_pulse_callback(self, chip, gpio, level, tick) -> None:   # type: ignore
        self.__pulse_count += 1  # increment the pulse count for that motor
    
    def __calculate_error(self, targetPWM: int, currentRPM: int) -> int:
        if targetPWM > 0:
            return targetPWM - currentRPM
        elif targetPWM < 0:
            return targetPWM + currentRPM
        return 0
        
    def pi_controller(self, targetPWM: int, motorSpeed: float) -> float:
        currentRPM = (self.pulse_count / 1080) * (60 / self.__DT)
       
        error = self.__calculate_error(targetPWM, int(currentRPM))
       
        adjustment = self.__KP * error
        motorSpeed = max(-1.0, min(1.0, motorSpeed + adjustment))
        self.pulse_count = 0
        return motorSpeed
        
     
        