
TRANSLATIONS = {
    'en': {
        'app_title': 'Comic Utilities',
        'tab_comic': 'Comic Folder to CBZ',
        'tab_ebook': 'Ebook (epub/mobi) to CBZ',
        'input_dir': 'Input Directory:',
        'output_dir': 'Output Directory:',
        'browse': 'Browse...',
        'start': 'Start Conversion',
        'log': 'Log:',
        'ready': 'Ready',
        'processing': 'Processing...',
        'done': 'Done',
        'error': 'Error',
        'select_input': 'Please select an input directory.',
        'input_not_exist': "Error: Input directory '{}' does not exist.",
        'add_files': 'Add Files',
        'remove_selected': 'Remove Selected',
        'clear_list': 'Clear List',
        'open_output': 'Open Output',
        'file_col': 'File',
        'type_col': 'Type',
        'status_col': 'Status',
        'status_pending': 'Pending',
        'status_converting': 'Converting',
        'status_success': 'Success',
        'status_failed': 'Failed',
        'msg_no_files': 'Please add files first',
        'msg_done_title': 'Done',
        'msg_done_count': 'Converted {} files',
        'msg_done_fail': 'Success {}, Failed {}\n{}',
        'progress_fmt': 'Progress: {}/{} (OK {}, Fail {})',
        'drag_drop_hint': 'Drag and drop files/folders here',
        'menu_language': 'Language',
        'menu_help': 'Help',
        'menu_about': 'About',
        'about_msg': 'Comic Utilities\n\nA unified toolset for comic book management.',
    },
    'zh': {
        'app_title': '漫画工具箱',
        'tab_comic': '文件夹转 CBZ',
        'tab_ebook': '电子书转 CBZ',
        'input_dir': '输入目录:',
        'output_dir': '输出目录:',
        'browse': '选择...',
        'start': '开始转换',
        'log': '日志:',
        'ready': '就绪',
        'processing': '处理中...',
        'done': '完成',
        'error': '错误',
        'select_input': '请选择输入目录。',
        'input_not_exist': "错误: 输入目录 '{}' 不存在。",
        'add_files': '添加文件',
        'remove_selected': '移除选中',
        'clear_list': '清空列表',
        'open_output': '打开输出目录',
        'file_col': '文件',
        'type_col': '类型',
        'status_col': '状态',
        'status_pending': '等待中',
        'status_converting': '转换中',
        'status_success': '成功',
        'status_failed': '失败',
        'msg_no_files': '请先添加文件',
        'msg_done_title': '完成',
        'msg_done_count': '已转换 {} 个文件',
        'msg_done_fail': '成功 {}, 失败 {}\n{}',
        'progress_fmt': '进度: {}/{} (成功 {}, 失败 {})',
        'drag_drop_hint': '将文件/文件夹拖拽至此',
        'menu_language': '语言',
        'menu_help': '帮助',
        'menu_about': '关于',
        'about_msg': '漫画工具箱\n\n一个统一的漫画管理工具集。',
    }
}

class I18n:
    def __init__(self):
        self.lang = 'zh' # Default to Chinese as requested "software need bilingual, but maybe default to system or zh" - user asked for bilingual support.
        self.listeners = []

    def set_lang(self, lang):
        if lang in TRANSLATIONS:
            self.lang = lang
            self.notify()

    def get(self, key, *args):
        text = TRANSLATIONS[self.lang].get(key, key)
        if args:
            return text.format(*args)
        return text

    def add_listener(self, listener):
        self.listeners.append(listener)
    
    def notify(self):
        for listener in self.listeners:
            listener()

# Global instance
i18n = I18n()
