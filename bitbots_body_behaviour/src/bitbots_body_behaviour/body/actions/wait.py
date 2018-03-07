"""
Wait
^^^^

.. moduleauthor:: Martin Poppinga <1popping@informatik.uni-hamburg.de>

Just waits for something (i.e. that preconditions will be fullfilled)
"""
import rospy

from bitbots_stackmachine.abstract_action_module import AbstractActionModule
from bitbots_common.connector.connector import BodyConnector


class Wait(AbstractActionModule):
    def __init__(self, connector: BodyConnector, args=99999999):
        super(Wait, self).__init__(connector)
        if args is None:
            args = 10
        self.time = rospy.get_time() + args

    def perform(self, connector, reevaluate=False):
        if connector.vision.ball_seen():
            connector.blackboard.set_head_duty("BALL_MODE")

        connector.walking.stop_walking()
        if self.time > rospy.get_time():
            self.pop()
