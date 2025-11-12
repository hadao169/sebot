import rclpy
from rclpy.node import Node

from nav_msgs.msg import Odometry
from tf_transformations import quaternion_from_euler

from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster

from motordriver_msgs.msg import MotordriverMessageBattery

import math

try:
    from .encoder import Encoder
except:
    from encoder import Encoder


class OdomNode(Node):
  def __init__(self):
    super().__init__('odom_battery_node')

    # Lue parametrit
    self.declare_parameter('wheel_radius', 0.1)
    self.declare_parameter('wheel_base', 0.5)
    self.declare_parameter('ticks_per_revolution', 1075)

    # Hae parametrien arvot
    self.wheel_radius = self.get_parameter('wheel_radius').value
    self.wheel_base = self.get_parameter('wheel_base').value
    self.ticks_per_revolution = self.get_parameter('ticks_per_revolution').value

    self.get_logger().info(f'Pyörän säde: {self.wheel_radius}')
    self.get_logger().info(f'Pyörien etäisyys: {self.wheel_base}')
    self.get_logger().info(f'Anturin kierros: {self.ticks_per_revolution}')

    ## Otetaan framelle etuliite parametrinä tai jos parametriä ei syötetä, otetaan se namespace-tiedosta.
    #self.declare_parameter('frame_prefix', '')
    #frame_prefix_param = self.get_parameter('frame_prefix').get_parameter_value().string_value
    #if frame_prefix_param:
    #    self.frame_prefix = frame_prefix_param + '_'
    #else:
    #    ns = self.get_namespace().strip('/')
    #    self.frame_prefix = f'{ns}_' if ns and ns != '' else ''

    #if self.frame_prefix:
    #        self.get_logger().info(f'Käytetään frame-etuliitettä: "{self.frame_prefix}"') 
    

    self.left_encoder = Encoder(self.wheel_radius, self.ticks_per_revolution)
    self.right_encoder = Encoder(self.wheel_radius, self.ticks_per_revolution)

    self.odom_theta = 0.0
    self.odom_x = 0.0
    self.odom_y = 0.0

    self.motor_subscriber = self.create_subscription(
        MotordriverMessageBattery,
        'motor_data',
        self.update_encoders_callback,
        10
    )

    self.odom_publisher = self.create_publisher(
        Odometry,
        'odom',
        10
    )

    # TransformBroadcaster tarvitsee viitteen pääluokkaan saadakseen tarvittavan kontekstin
    # (noden  asetukset tai muun jaetun datan). Tämä tapahtuu antamalla self parametrina.
    self.tf_broadcaster = TransformBroadcaster(self)

    self.prev_time = self.get_clock().now().nanoseconds

    timer_period = 0.1 # Sekuntia
    self.timer = self.create_timer(timer_period, self.timer_callback)
    self.update = True

  def update_encoders_callback(self, message):
    # Tallennetaan messagessa olevat tiedot, jotta niitä voidaan käsitellä timer_callback:ssa
    self.left_encoder.update(message.encoder1)
    self.right_encoder.update(-message.encoder2)
    self.update = True

  def timer_callback(self):
    if not self.update: return
    self.update = False
    current_time = self.get_clock().now().nanoseconds
    elapsed = (current_time - self.prev_time)/1000000000
    self.prev_time = current_time

    d_left= self.left_encoder.deltam()
    d_right = self.right_encoder.deltam()

    # Kuljettu matka (delta_distance) lasketaan ottamalla vasemman ja oikean pyörän kulkema matka
    # jaettuna kahdella. Robotin liikkuma matka suoraviivaisesti keskilinjan (robottia keskeltä
    # halkova akseli) pitkin.
    # Kulman muutos (delta_theta) lasketaan ottamalla vasemman ja oikean pyörän kulkeman matkan erotus ja
    # jakamalla se pyörien välisellä etäisyydellä
    # Jos pyörät liikkuvat yhtä paljon samaan suuntaan (𝑑_left=𝑑_right -> delta_theta=0), robotti liikkuu
    # suoraan eteen- tai taaksepäin.
    # Jos pyörät liikkuvat yhtä paljon erisuuntiin (𝑑_left=-𝑑_right -> delta_distance=0), robotti pyörii
    # paikallaan
    delta_distance = (d_left + d_right) / 2.0
    delta_theta = (d_left - d_right) / self.wheel_base

    if delta_distance != 0:
      robot_x = math.cos( delta_theta ) * delta_distance
      robot_y = -math.sin( delta_theta ) * delta_distance
      self.odom_x = self.odom_x + ( math.cos( self.odom_theta ) * robot_x - math.sin( self.odom_theta ) * robot_y )
      self.odom_y = self.odom_y + ( math.sin( self.odom_theta ) * robot_x + math.cos( self.odom_theta ) * robot_y )

    linear_y = delta_distance * math.cos(self.odom_theta) / elapsed
    linear_x = delta_distance * math.sin(self.odom_theta) / elapsed
    angular_z = delta_theta / elapsed

    self.odom_theta = delta_theta + self.odom_theta

    odom_msg = Odometry()
    odom_msg.header.stamp = self.get_clock().now().to_msg()
    #odom_msg.header.frame_id = self.frame_prefix + 'odom' # Lisätään framen nimen eteen namespacen (tai parametrin) mukainen etuliite.
    #odom_msg.child_frame_id = self.frame_prefix + 'base_footprint'
    odom_msg.header.frame_id = 'odom'
    odom_msg.child_frame_id = 'base_footprint'

    # pose sisältää kaksi osaa:
    # position (geometry_msgs/Point)
    #  x, y, z: Robotin sijainti koordinaatistossa.
    # orientation (geometry_msgs/Quaternion)
    #  x, y, z, w: Robotin orientaatio quaternion-muodossa (3D-rotaatio).
    odom_msg.pose.pose.position.x = self.odom_x ##
    odom_msg.pose.pose.position.y = self.odom_y ##
    odom_msg.pose.pose.position.z = 0.0

    quat = quaternion_from_euler(0.0, 0.0, self.odom_theta)
    odom_msg.pose.pose.orientation.x = quat[0] ##
    odom_msg.pose.pose.orientation.y = quat[1] ##
    odom_msg.pose.pose.orientation.z = quat[2] ##
    odom_msg.pose.pose.orientation.w = quat[3] ##

    # Nopeudet (valinnainen, ei käytössä tässä sovelluksessa)
    odom_msg.twist.twist.linear.x = linear_x
    odom_msg.twist.twist.linear.y = linear_y
    odom_msg.twist.twist.angular.z = angular_z

    # Julkaistaan odometry viesti
    self.odom_publisher.publish(odom_msg) ##

    t = TransformStamped()
    t.header.stamp = self.get_clock().now().to_msg()
    #t.header.frame_id = self.frame_prefix + 'odom'
    #t.child_frame_id = self.frame_prefix + 'base_footprint'
    t.header.frame_id = 'odom'
    t.child_frame_id = 'base_footprint'

    t.transform.translation.x = self.odom_x ##
    t.transform.translation.y = self.odom_y ##
    t.transform.translation.z = 0.0

    # z: Quaternionin osa, joka liittyy rotaatioon  z-akselin suuntaan. Tämä ei yksinään ole kulma,
    # vaan osa rotaation akselin ja kulman yhteistä esitystä.
    # w: Quaternionin skaalarikomponentti, joka määrittää, kuinka suuri osa rotaatiosta tulee akselin
    # ympäriltä. Suhteessa muihin quaternion-komponentteihin, tämä määrittää kulman.

    t.transform.rotation.z = math.sin(self.odom_theta / 2.0) ##
    t.transform.rotation.w = math.cos(self.odom_theta / 2.0) ##

    # Julkaistaan transformaatio
    self.tf_broadcaster.sendTransform(t) ##


def main(args=None):
  rclpy.init(args=args)

  odom_node = OdomNode()

  try:
    rclpy.spin(odom_node)
  except KeyboardInterrupt:
    pass
  finally:
    odom_node.destroy_node()
    if rclpy.ok():
      rclpy.shutdown()

if __name__ == '__main__':
  main()