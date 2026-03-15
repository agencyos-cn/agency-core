"""Base Device Class Definition"""

class DeviceBase:
    """设备基类，所有具体设备需要继承此类"""
    
    def __init__(self, device_id, device_type, name="", description=""):
        """初始化设备
        
        Args:
            device_id (str): 设备唯一标识符
            device_type (str): 设备类型
            name (str): 设备名称
            description (str): 设备描述
        """
        self.device_id = device_id
        self.device_type = device_type
        self.name = name
        self.description = description
        self.is_connected = False
    
    def connect(self):
        """连接设备
        
        Raises:
            NotImplementedError: 子类必须实现此方法
        """
        raise NotImplementedError("Subclasses must implement connect method")
    
    def disconnect(self):
        """断开设备连接
        
        Raises:
            NotImplementedError: 子类必须实现此方法
        """
        raise NotImplementedError("Subclasses must implement disconnect method")
    
    def send_command(self, command, *args, **kwargs):
        """向设备发送命令
        
        Args:
            command (str): 命令
            *args: 命令参数
            **kwargs: 命令关键字参数
            
        Raises:
            NotImplementedError: 子类必须实现此方法
        """
        raise NotImplementedError("Subclasses must implement send_command method")
    
    def is_available(self):
        """检查设备是否可用
        
        Returns:
            bool: 设备是否可用
        """
        return self.is_connected