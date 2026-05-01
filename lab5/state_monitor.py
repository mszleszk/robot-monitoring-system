import rclpy
from rclpy.node import Node

from std_msgs.msg import Bool
from interfaces.srv import ComponentError

class StateMonitor(Node):
   
   def __init__(self):
      super().__init__('state_monitor')

      self.declare_parameter('sensors', ['sensor'])
      self.declare_parameter('timeout', 2.0)
      self.declare_parameter('robot_state_timer_period', 1.0)

      self.sensors = self.get_parameter('sensors').value
      self.timeout = self.get_parameter('timeout').value
      self.robot_state_timer_period = self.get_parameter('robot_state_timer_period').value

      self.publisher = self.create_publisher(Bool, 'robot_state', 10)

      self.robot_state_timer = self.create_timer(self.robot_state_timer_period, self.robot_state_timer_callback)

      self.subs = []

      for sensor in self.sensors:
         sub = self.create_subscription(
            Bool, 
            f'{sensor}_state', 
            lambda msg, sensor_name=sensor: self.listener_callback(msg, sensor_name), 
            10
         )

         self.subs.append(sub)

      self.state_check_timer = self.create_timer(self.timeout, self.state_check_timer_callback)
      self.states = {sensor: True for sensor in self.sensors}

      self.client = self.create_client(ComponentError, 'component_error')


   def listener_callback(self, msg, sensor):
      self.states[sensor] = msg.data

      # self.get_logger().info(f'I heard: {msg.data} from {sensor}')

      if msg.data == False:
         self.get_logger().info(f'False heard from {sensor}. Notifying error handler')
         self.notify_error_handler(sensor)


   def state_check_timer_callback(self):
      for sensor, state in self.states.items():
         if state == False:
            self.get_logger().info(f"No state message from {sensor}. Notifying error handler.")
            self.notify_error_handler(sensor)

         self.states[sensor] = False


   def robot_state_timer_callback(self):
      msg = Bool()

      msg.data = True

      for _, state in self.states.items():
         if state == False:
            msg.data = False

      self.publisher.publish(msg)
      self.get_logger().info(f'Publishing: {msg.data}')


   def notify_error_handler(self, sensor):
      if not self.client.wait_for_service(timeout_sec=1.0):
         return 
      
      req = ComponentError.Request()
      req.sensor_name = sensor
      
      self.client.call_async(req)


def main():
   rclpy.init()

   state_monitor = StateMonitor()

   rclpy.spin(state_monitor)

   state_monitor.destroy_node()
   rclpy.shutdown()