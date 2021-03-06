# -*- coding:utf-8 -*-
import json
from bitbots_stackmachine.abstract_stack_element import AbstractStackElement

class AbstractDecisionElement(AbstractStackElement):
    """
        The logic is encapsulated in two types of elements. 
        The decision elements define the logical path similar to a behavior tree. 
        Corresponding decisions can be as complex as wished, using in the most simple case if-else clauses or in a more complicated situation, for example, neural networks. 
        Either way, one decision-element should capsule one logical decision and determine the following module, without giving any calls to the hardware level.
        One example is the decision if the robot has sufficient knowledge about the current ball position, using data from the vision components and the team-communication.
        By using a push method they add further elements to the stack. 
        Thereby, each decision element can have other decision or actions as following active elements. 
        All decisions can, therefore, be displayed as a decision tree.
    """

    _reevaluate = False

    def __repr__(self):
        """
        Overlaod from the AbstractStackElement to have "Decision" at the start.
        """
        shortname = self.__class__.__name__

        data = json.dumps(self.debug_data)
        self.debug_data = {}

        return "<Decision: %s>[%s]" % (shortname, data)


    def push(self, element, init_data=None, perform=True):
            """        
            Help method for easy pushing on the stack.

            Should normally called with a return::
                return self.push(NewElement, data)

            If no return is used, there is code execution after the push which leads to difficult to debug behavior.
            This should only be done if you want to push multiple actions as a sequence. But then the last push should also have a return.


            :param element: The element which should be put on the stack
            :type element: Class, inheritate from AbstractStacklement
            :param init_data: Data which is given to the class on init
            :type init_data: object
            """
            self._behaviour.push(element, init_data, perform)


    def push_action_sequence(self, SequenceElement, actions, init_datas):
        """
        Small helper method to push action sequences
        """
        dic = {"actions": actions, "action_datas": init_datas}
        self.push(SequenceElement, dic)


    def get_reevaluate(self):
        """
        Each decision element may define a \textit{reevaluate} criteria.
        If the corresponding method returns true, the element will be executed even if it is in the middle of the stack. 
        This way a precondition can be checked, for example, every tenth iteration. 
        As an example, every iteration it could be checked if the ball position is known to the robot with a given certainty. 
        If the now pushed element is different from the element which is currently above in the stack, the whole stack above will be dropped and the newly selected element executed.

        This method returns if the element should be reevaluated. This means that the element is recomputed even if it is not on top of the stack. 
        If the decision pushes a different element than in the original perform, the stack above this decision is cleared. 
        This can be used to regulary check preconditions, e.g. if the robot knows where the ball is.
        """
        return self._reevaluate

    