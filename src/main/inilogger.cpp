#include "inilogger.hpp"

void IniLogger::log(spdlog::level::level_enum level, const std::string& message) {
  if(IniLogger::mainLogger == nullptr) {
    IniLogger::mainLogger = spdlog::stdout_logger_st("main");
    IniLogger::mainLogger->set_pattern("[%Y-%m-%d %H:%M:%S.%e] [json2pdf] [%n] [%l] %v");
  }

  IniLogger::mainLogger->log(level, message);
}