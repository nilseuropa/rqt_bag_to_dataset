cmake_minimum_required(VERSION 2.8.3)
project(rqt_bag_to_dataset)

find_package(catkin REQUIRED
)

catkin_package(
    CATKIN_DEPENDS
)

catkin_python_setup()

#############
## Install ##
#############

install(FILES plugin.xml
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)

install(DIRECTORY resource
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)

install(PROGRAMS scripts/bag_to_dataset
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
