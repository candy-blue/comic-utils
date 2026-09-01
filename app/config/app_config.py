from qfluentwidgets import (
    QConfig, ConfigItem, OptionsConfigItem, RangeConfigItem,
    OptionsValidator, RangeValidator, BoolValidator
)

class AppConfig(QConfig):
    # Pack & Convert
    packFormat = OptionsConfigItem(
        "Pack", "Format", "cbz", OptionsValidator(["cbz", "zip", "pdf", "epub", "7z"])
    )
    convertFormat = OptionsConfigItem(
        "Convert", "Format", "cbz", OptionsValidator(["cbz", "zip", "pdf", "epub", "7z"])
    )

    # General & Appearance
    language = OptionsConfigItem(
        "General", "Language", "zh", OptionsValidator(["zh", "en"])
    )
    concurrentTasks = OptionsConfigItem(
        "Processing", "Concurrent", "2", OptionsValidator(["1", "2", "3", "4"])
    )
    autoCheckUpdate = ConfigItem(
        "Update", "AutoCheck", True, BoolValidator()
    )

    # AI Engine Settings
    aiProvider = OptionsConfigItem(
        "AI", "Provider", "openai_compatible", OptionsValidator(["openai_compatible", "google_gemini"])
    )
    aiBaseUrl = ConfigItem(
        "AI", "BaseUrl", "https://api.deepseek.com/v1"
    )
    aiApiKey = ConfigItem(
        "AI", "ApiKey", ""
    )
    aiModelName = ConfigItem(
        "AI", "ModelName", "deepseek-chat"
    )
    aiTemplate = ConfigItem(
        "AI", "Template", "[{author}] {title} - Vol.{vol:02d} [{group}]"
    )
    aiAutoComicInfo = ConfigItem(
        "AI", "AutoComicInfo", True, BoolValidator()
    )

    # Manga Optimizer Settings
    optPreset = OptionsConfigItem(
        "Optimizer", "Preset", "extreme_webp", OptionsValidator(["extreme_webp", "balanced_jpeg", "custom"])
    )
    optTargetFormat = OptionsConfigItem(
        "Optimizer", "TargetFormat", "webp", OptionsValidator(["webp", "jpeg", "png", "original"])
    )
    optQuality = RangeConfigItem(
        "Optimizer", "Quality", 75, RangeValidator(1, 100)
    )
    optCoverQuality = RangeConfigItem(
        "Optimizer", "CoverQuality", 88, RangeValidator(1, 100)
    )
    optMaxDimension = OptionsConfigItem(
        "Optimizer", "MaxDimension", "2160", OptionsValidator(["0", "1920", "2160", "2560", "3840"])
    )
    optAutoGrayscale = ConfigItem(
        "Optimizer", "AutoGrayscale", True, BoolValidator()
    )
    optOutputMode = OptionsConfigItem(
        "Optimizer", "OutputMode", "suffix", OptionsValidator(["suffix", "overwrite", "new_folder"])
    )
    optOutputFolder = ConfigItem(
        "Optimizer", "OutputFolder", ""
    )
    optKeepBackup = ConfigItem(
        "Optimizer", "KeepBackup", True, BoolValidator()
    )

cfg = AppConfig()
