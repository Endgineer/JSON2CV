#include "inilogger.hpp"
#include "argparser.hpp"
#include "dllupdater.hpp"
#include "thddispatcher.hpp"

int main(int argc, char *argv[]) {
  IniLogger::log(spdlog::level::info, "Initialized logger");
  
  const std::string *currentCompilerVersion = ArgParser::init(argc, argv);

  DllUpdater::update(currentCompilerVersion);

  ThdDispatcher::dispatch(ArgParser::get());

  ThdDispatcher::join();

  ArgParser::clean();

  return 0;
}
