import lgpio
import time

class Encoder:

    __KP = 0.0005
    __DT = 0.05

    def __init__(self, aPin : int, aChip ) -> None:
        self.__pin = aPin
        self.__chip = aChip
        self.__pulse_count = 0
        
        self.__last_time = time.time()
        
        lgpio.gpio_claim_alert(self.__chip, self.__pin, lgpio.BOTH_EDGES, lgpio.SET_PULL_UP) # claim the GPIO pin for input lgpio.gpio_set_mode(chip, pin, lgpio.GPIO_MODE_INPUT) # set the pin as input lgpio.gpio_set_pull(chip, pin, lgpio.GPIO_PULL_UP) # enable pull-up resistor lgpio.gpio_set_alert_func(chip, pin, count_pulse_callback) # set the interrupt handler for this pin
        lgpio.callback(self.__chip, self.__pin, lgpio.BOTH_EDGES, func=self.__count_pulse_callback) # register the callback function for both rising and falling edges

    # chip = gpiochip, gpio = pin number, level = 0 or 1, tick = timestamp of event
    def __count_pulse_callback(self, chip, gpio, level, tick) -> None:   # type: ignore
        self.__pulse_count += 1  # increment the pulse count for that motor
        
    def reset_count(self):
        self.__pulse_count = 0
    
    

    def pi_controller(self, target_rpm: int, current_throttle: float) -> float:
        now = time.time()
        actual_dt = now - self.__last_time # Measure how long it ACTUALLY took
        self.__last_time = now
        
        if actual_dt <= 0: actual_dt = 0.05 # Safety check
        
        # Use actual_dt instead of the hardcoded 0.05
        current_rpm = (self.__pulse_count / 1080.0) * (60.0 / actual_dt)
        
        # 2. Use absolute values for the error, then re-apply direction
        # This prevents the "fighting" logic
        error = abs(target_rpm) - current_rpm
        
        # 3. If target is negative, error should move throttle further negative
        direction = 1 if target_rpm >= 0 else -1
        adjustment = (self.__KP * error) * direction
        
        new_throttle = max(-1.0, min(1.0, current_throttle + adjustment))
        
        print(f"Pulses: {self.__pulse_count} | Err: {error} | RPM: {current_rpm}/{target_rpm} | Throttle: {new_throttle}")
        
        
        self.reset_count()
        return new_throttle 
        
    # def pi_controller(self, target_rpm: int, current_throttle: float) -> float:
    #     current_rpm = (self.__pulse_count / 1080) * (60 / self.__DT)
        
    #     if target_rpm > 0:
    #         error = target_rpm - current_rpm
    #     elif target_rpm < 0:
    #         error = target_rpm + current_rpm
    #     else:
    #         error = 0
        
    #     adjustment = self.__KP * error
        
    #     new_throttle = max(-1.0, min(1.0, current_throttle + adjustment))
        
        
    #     self.reset_count()
    #     return new_throttle
    
        
    
        