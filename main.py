import logging
import logging.config

import model.log_config

log_config = model.log_config.LogConfig()
print(log_config.factory())
logging.config.dictConfig(log_config.factory())
a = logging.getLogger("a")
a.info("info")
a.error("error")
a.critical("critical")
a.debug("debug")
a.warning("warning")
