"""
WorldModellCapsule
^^^^^^^^^^^^^^^^^^

Provides informations about the world model.

"""
import math

import rospy
import tf2_ros as tf2
from tf2_geometry_msgs import PointStamped
from tf.transformations import euler_from_quaternion
from humanoid_league_msgs.msg import Position2D, ObstaclesRelative, GoalRelative


class WorldModelCapsule:
    def __init__(self, config):
        self.position = Position2D()
        self.tf_buffer = tf2.Buffer(cache_time=rospy.Duration(5.0))
        self.tf_listener = tf2.TransformListener(self.tf_buffer)
        self.ball = PointStamped()  # The ball in the base footprint frame
        self.goal = GoalRelative()
        self.obstacles = ObstaclesRelative()
        self.my_data = dict()
        self.counter = 0
        self.field_length = config["Body"]["Common"]["Field"]["length"]
        self.goal_width = config["Body"]["Common"]["Field"]["length"]

    def get_current_position(self):
        return self.position.pose.x, self.position.pose.y, self.position.pose.theta

    ############
    # ## Ball ##
    ############

    def ball_seen(self):
        return rospy.get_time() - self.ball_last_seen() < 0.5

    def ball_last_seen(self):
        return self.my_data.get("BallLastSeen", -999)

    def get_ball_position_xy(self):
        """Calculate the absolute position of the ball"""
        u, v = self.get_ball_position_uv()
        return self.get_xy_from_uv(u, v)

    def get_ball_stamped(self):
        return self.ball

    def get_ball_position_uv(self):
        return self.ball.point.x, self.ball.point.y

    def get_ball_distance(self):
        u, v = self.get_ball_position_uv()
        return math.sqrt(u ** 2 + v ** 2)

    def get_ball_speed(self):
        raise NotImplementedError

    def ball_callback(self, ball):
        if ball.confidence == 0:
            return

        ball_stamped = PointStamped(ball.header, ball.ball_relative)
        try:
            self.ball = self.tf_buffer.transform(ball_stamped, 'base_footprint', timeout=rospy.Duration(0.3))
        except (tf2.ConnectivityException, tf2.LookupException, tf2.ExtrapolationException):
            return
        self.my_data["BallLastSeen"] = rospy.get_time()

    ###########
    # ## Goal #
    ###########

    def any_goal_seen(self):
        return rospy.get_time() - self.any_goal_last_seen() < 0.5

    def any_goal_last_seen(self):
        # We are currently not seeing any goal, we know where they are based
        # on the localisation. Therefore, any_goal_last_seen returns the time
        # from the stamp of the last position update
        return self.position.header.stamp.to_time()

    def get_opp_goal_center_uv(self):
        x, y = self.get_opp_goal_center_xy()
        return self.get_uv_from_xy(x, y)

    def get_opp_goal_center_xy(self):
        return self.field_length / 2, 0

    def get_own_goal_center_uv(self):
        x, y = self.get_own_goal_center_xy()
        return self.get_uv_from_xy(x, y)

    def get_own_goal_center_xy(self):
        return -self.field_length / 2, 0

    def get_opp_goal_angle_from_ball(self):
        ball_x, ball_y = self.get_ball_position_xy()
        goal_x, goal_y = self.get_opp_goal_center_xy()
        return math.atan2(goal_y - ball_y, goal_x - ball_x)

    def get_opp_goal_distance(self):
        x, y = self.get_opp_goal_center_xy()
        return self.get_distance_to_xy(x, y)

    def get_opp_goal_left_post_uv(self):
        x, y = self.get_opp_goal_center_xy()
        return self.get_uv_from_xy(x, y - self.goal_width / 2)

    def get_opp_goal_right_post_uv(self):
        x, y = self.get_opp_goal_center_xy()
        return self.get_uv_from_xy(x, y + self.goal_width / 2)

    def goal_callback(self):
        # Currently not used
        pass

    #############
    # ## Common #
    #############

    def get_uv_from_xy(self, x, y):
        """ Returns the relativ positions of the robot to this absolute position"""
        current_position = self.get_current_position()
        x2 = x - current_position[0]
        y2 = y - current_position[1]
        theta = -1 * current_position[2]
        u = math.cos(theta) * x2 + math.sin(theta) * y2
        v = math.cos(theta) * y2 - math.sin(theta) * x2
        return u, v

    def get_xy_from_uv(self, u, v):
        """ Returns the absolute position from the given relative position to the robot"""
        pos_x, pos_y, theta = self.get_current_position()
        angle = math.atan2(v, u) + theta
        hypotenuse = math.sqrt(u ** 2 + v ** 2)
        return pos_x + math.sin(angle) * hypotenuse, pos_y + math.cos(angle) * hypotenuse

    def get_distance_to_xy(self, x, y):
        """ Returns distance from robot to given position """
        u, v = self.get_uv_from_xy(x, y)
        dist = math.sqrt(u ** 2 + v ** 2)
        return dist

    def position_callback(self, pos):
        # Convert PositionWithCovarianceStamped to Position2D
        position2d = Position2D()
        position2d.header = pos.header
        position2d.pose.x = pos.pose.pose.position.x
        position2d.pose.y = pos.pose.pose.position.y
        rotation = pos.pose.pose.orientation
        position2d.pose.theta = euler_from_quaternion([rotation.x, rotation.y, rotation.z, rotation.w])[2]
        self.position = position2d
