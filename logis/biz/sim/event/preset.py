from logis.data_type import EventType

ORDER_STARTED = EventType("order_started")
ORDER_FINISHED = EventType("order_finished")
TASK_STARTED = EventType("task_started")
TASK_FINISHED = EventType("task_finished")
MATERIAL_READY = EventType("material_ready")
STOCK_ARRIVED = EventType("stock_arrived")
PRODUCT_READY = EventType("product_ready")
BLUEPRINT_DONE = EventType("blueprint_done")
STOCK_CREATED = EventType("stock_created")
STOCK_DELETED = EventType("stock_deleted")
RECORD_CREATE_STOCK = EventType("add_stock")
RECORD_DELETE_STOCK = EventType("remove_stock")
RECORD_MOVING = EventType("add_movement")
RECORD_UNLOADING = EventType("add_unloading")
RECORD_LOADING = EventType("add_loading")
RECORD_LIFTING = EventType("add_lifting")
RECORD_LOWING = EventType("add_lowering")
SYSTEM_EXIT = EventType("system_exit")  # 蓝图退出事件

STOCK_STORED = EventType("stock_stored")
STOCK_RETRIEVED = EventType("stock_retrieved")
STAGE_FINISHED = EventType("stage_finished")
