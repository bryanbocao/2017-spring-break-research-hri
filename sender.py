#!/usr/bin/env python
__author__ = 'flier'
import rospy
import leap_interface
from leap_motion.msg import leap
from leap_motion.msg import leapros
from geometry_msgs.msg import Twist

# Obviously, this method publishes the data defined in leapros.msg to /leapmotion/data
def sender():
    li = leap_interface.Runner()
    li.setDaemon(True)
    li.start()
    # pub     = rospy.Publisher('leapmotion/raw',leap)
    pub_ros   = rospy.Publisher('leapmotion/data',leapros)
    cmd_pub = rospy.Publisher('cmd_vel_mux/input/teleop', Twist, queue_size=5)
    rospy.init_node('leap_pub')

    while not rospy.is_shutdown():
        hand_direction_   = li.get_hand_direction()
        hand_normal_      = li.get_hand_normal()
        hand_palm_pos_    = li.get_hand_palmpos()
        hand_pitch_       = li.get_hand_pitch()
        hand_roll_        = li.get_hand_roll()
        hand_yaw_         = li.get_hand_yaw()
        is_hand_ = li.get_is_hand()
        msg = leapros()
        msg.direction.x = hand_direction_[0]
        msg.direction.y = hand_direction_[1]
        msg.direction.z = hand_direction_[2]
        msg.normal.x = hand_normal_[0]
        msg.normal.y = hand_normal_[1]
        msg.normal.z = hand_normal_[2]
        msg.palmpos.x = hand_palm_pos_[0]
        msg.palmpos.y = hand_palm_pos_[1]
        msg.palmpos.z = hand_palm_pos_[2]
        msg.ypr.x = hand_yaw_
        msg.ypr.y = hand_pitch_
        msg.ypr.z = hand_roll_

        moveBindings = {
            'n':(1,0),
            'ne':(1,-1),
            'w':(0,1),
            'e':(0,-1),
            'nw':(1,1),
            's':(-1,0),
            'se':(-1,1),
            'sw':(-1,-1),
               }
        #TODO: Adjust movement parameters
        if is_hand_ == True:
            print "THERE IS A HAND"
            if msg.ypr.y < .2 and msg.ypr.y >-.2: #PITCH FOR LINEAR MOVEMENT
                print "NO LINEAR MOVEMENT"
                x = 0
            elif msg.ypr.y > .2:
                print "FORWARD"
                x = 1
            elif msg.ypr.y <-.2:
                print "BACKWARD"
                x = -1
            if msg.ypr.x < .2 and msg.ypr.x >-.2: #ROLL FOR ANGULAR MOVEMENT
                print "NO ANGULAR MOVEMENT"
                th = 0
            elif msg.ypr.x > .2:
                print "RIGHT"
                th = -1
            elif msg.ypr.x <-.2:
                print "LEFT"
                th = 1

            x_move = .1 * x
            th_move = .1 * th

            twist = Twist()
            twist.linear.x = x_move; twist.linear.y = 0; twist.linear.z = 0
            twist.angular.x = 0; twist.angular.y = 0; twist.angular.z = th_move
            cmd_pub.publish(twist)
        else:
            twist = Twist()
            twist.linear.x = 0; twist.linear.y = 0; twist.linear.z = 0
            twist.angular.x = 0; twist.angular.y = 0; twist.angular.z = 0
            cmd_pub.publish(twist)


        # We don't publish native data types, see ROS best practices
        # pub.publish(hand_direction=hand_direction_,hand_normal = hand_normal_, hand_palm_pos = hand_palm_pos_, hand_pitch = hand_pitch_, hand_roll = hand_roll_, hand_yaw = hand_yaw_)
        pub_ros.publish(msg)
        # Save some CPU time, circa 100Hz publishing.
        rospy.sleep(0.01)


if __name__ == '__main__':
    try:
        sender()
    except rospy.ROSInterruptException:
        pass
