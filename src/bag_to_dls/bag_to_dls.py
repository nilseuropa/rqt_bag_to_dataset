from __future__ import division
import os

import rospy
import roslib
import rospkg
import rosbag

from python_qt_binding import loadUi
from python_qt_binding.QtCore import QFile, QIODevice, QObject, Qt, Signal
from python_qt_binding.QtGui import QIcon, QImage, QPainter
from python_qt_binding.QtWidgets import QFileDialog, QGraphicsScene, QWidget, QTreeWidgetItem, QHeaderView, QMenu, QTreeWidgetItem

class RosBagToDataset(QObject):

    _deferred_fit_in_view = Signal()
    _column_names = ['topic', 'type', 'buffer_size']

    def __init__(self, context):
        super(RosBagToDataset, self).__init__(context)
        self.initialized = False
        self._current_topic_list = []
        self._topics = {}
        self._tree_items = {}
        self._column_index = {}
        for column_name in self._column_names:
            self._column_index[column_name] = len(self._column_index)

        self.setObjectName('RosBagToDataset')

        self._widget = QWidget()

        rp = rospkg.RosPack()
        ui_file = os.path.join(rp.get_path('rqt_bag_to_dataset'), 'resource', 'RosBagToDataset.ui')
        loadUi(ui_file, self._widget)
        self._widget.setObjectName('RosBagToDatasetUi')
        if context.serial_number() > 1:
            self._widget.setWindowTitle(self._widget.windowTitle() + (' (%d)' % context.serial_number()))

        self._widget.topics_tree_widget.sortByColumn(0, Qt.AscendingOrder)

        self._widget.load_bag_push_button.setIcon(QIcon.fromTheme('document-open'))
        self._widget.load_bag_push_button.pressed.connect(self._load_bag)

        # self._widget.input_conf_push_button.setIcon(QIcon.fromTheme('document-new'))
        self._widget.input_conf_push_button.pressed.connect(self._configue_inputs)

        # self._widget.output_conf_push_button.setIcon(QIcon.fromTheme('applications-other'))
        self._widget.output_conf_push_button.pressed.connect(self._configue_outputs)

        # self._widget.check_conf_push_button.setIcon(QIcon.fromTheme('applications-science'))
        self._widget.check_conf_push_button.pressed.connect(self._check_config)

        self._widget.save_dls_push_button.setIcon(QIcon.fromTheme('document-save-as'))
        self._widget.save_dls_push_button.pressed.connect(self._save_dataset)

        context.add_widget(self._widget)

        self._force_refresh = False

    def shutdown_plugin(self):
        pass

    def save_settings(self, plugin_settings, instance_settings):
        # instance_settings.set_value(k, v)
        pass

    def restore_settings(self, plugin_settings, instance_settings):
        # v = instance_settings.value(k)
        pass

    def _generate_tool_tip(self, url):
        return url


    def _configue_inputs(self):
        pass

    def _configue_outputs(self):
        pass

    def _check_config(self):
        pass


    def _extract_array_info(self, type_str):
        array_size = None
        if '[' in type_str and type_str[-1] == ']':
            type_str, array_size_str = type_str.split('[', 1)
            array_size_str = array_size_str[:-1]
            if len(array_size_str) > 0:
                array_size = int(array_size_str)
            else:
                array_size = 0
        return type_str, array_size

    def _recursive_create_widget_items(self, parent, topic_name, type_name, message):

        if parent is self._widget.topics_tree_widget:
            topic_text = topic_name
            item = QTreeWidgetItem(parent)
        else:
            topic_text = topic_name.split('/')[-1]
            if '[' in topic_text:
                topic_text = topic_text[topic_text.index('['):]
            item = TreeWidgetItem(self._toggle_monitoring, topic_name, parent)

        item.setText(self._column_index['topic'], topic_text)
        item.setText(self._column_index['type'], type_name)
        item.setText(self._column_index['buffer_size'], "1")
        item.setData(0, Qt.UserRole, topic_name)

        self._tree_items[topic_name] = item
        # slots: message types that compose the parent message
        if hasattr(message, '__slots__') and hasattr(message, '_slot_types'):
            for slot_name, type_name in zip(message.__slots__, message._slot_types):
                self._recursive_create_widget_items(
                item, topic_name + '/' + slot_name, type_name, getattr(message, slot_name))

        else:
            base_type_str, array_size = self._extract_array_info(type_name)
            try:
                base_instance = roslib.message.get_message_class(base_type_str)()
            except (ValueError, TypeError):
                base_instance = None
            if array_size is not None and hasattr(base_instance, '__slots__'):
                for index in range(array_size):
                    self._recursive_create_widget_items(
                        item, topic_name + '[%d]' % index, base_type_str, base_instance)
        return item

    def _toggle_monitoring(self, topic_name):
        item = self._tree_items[topic_name]
        if item.checkState(0):
            print("Selected: "+topic_name)
        else:
            print("Deselected: "+topic_name)

    def _load_bag(self, file_name=None):
        if file_name is None:
            file_name, _ = QFileDialog.getOpenFileName(
                self._widget,
                self.tr('Open bag file'),
                None,
                self.tr('ROSbag file (*.bag)'))
            if file_name is None or file_name == '':
                return
        try:
            bag = rosbag.Bag(file_name)
            topics = bag.get_type_and_topic_info()[1].keys()
            types = []
            for i in range(0,len(bag.get_type_and_topic_info()[1].values())):
                types.append(list(bag.get_type_and_topic_info()[1].values())[i][0])

            for topic_name, topic_type in zip(topics,types):
                topic_item = self._recursive_create_widget_items(
                    self._widget.topics_tree_widget, topic_name, topic_type, roslib.message.get_message_class(topic_type) )

            self._widget.topics_tree_widget.header().setSectionResizeMode(QHeaderView.ResizeToContents)
            self._widget.topics_tree_widget.header().setStretchLastSection(True)

        except IOError:
            return


    def _fit_in_view(self):
        self._widget.graphics_view.fitInView(self._scene.itemsBoundingRect(),
                                             Qt.KeepAspectRatio)


    def _save_dataset(self):
        file_name, _ = QFileDialog.getSaveFileName(self._widget,
                                                   self.tr('Save as CSV'),
                                                   'dataset.csv',
                                                   self.tr('Dataset file (*.csv)'))
        if file_name is None or file_name == '':
            return

        file = QFile(file_name)
        if not file.open(QIODevice.WriteOnly | QIODevice.Text):
            return

        # file.write(self._dataset_file)
        file.close()


class TreeWidgetItem(QTreeWidgetItem):

    def __init__(self, check_state_changed_callback, topic_name, parent=None):
        super(TreeWidgetItem, self).__init__(parent)
        self._check_state_changed_callback = check_state_changed_callback
        self._topic_name = topic_name
        self.setCheckState(0, Qt.Unchecked)

    def setData(self, column, role, value):
        if role == Qt.CheckStateRole:
            state = self.checkState(column)
        super(TreeWidgetItem, self).setData(column, role, value)
        if role == Qt.CheckStateRole and state != self.checkState(column):
            self._check_state_changed_callback(self._topic_name)

    def __lt__(self, other_item):
        column = self.treeWidget().sortColumn()
        return super(TreeWidgetItem, self).__lt__(other_item)
