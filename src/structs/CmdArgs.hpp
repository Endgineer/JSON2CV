#ifndef CMDARGS_HPP
#define CMDARGS_HPP

#include <argparse/argparse.hpp>

struct Args : public argparse::Args {
  bool &version = flag("v,version", "Display current version").set_default(false);
  bool &update = flag("u,update", "Check for updates").set_default(false);

  std::optional<std::string> &cvJson = kwarg("cv,cvjson", "Path to cv json");
  std::optional<std::string> &clJson = kwarg("cl,cljson", "Path to cl json");

  std::optional<std::string> &varName = kwarg("n,name", "Name");
  std::optional<std::vector<std::string>> &varTitles = kwarg("t,titles", "Titles").multi_argument();
  std::optional<std::string> &varAddress = kwarg("a,address", "Address");
  std::optional<std::string> &varMobile = kwarg("m,mobile", "Mobile");
  std::optional<std::string> &varEmail = kwarg("e,email", "Email");
  std::optional<std::string> &varLinkedin = kwarg("l,linkedin", "Linkedin");
  std::optional<std::string> &varGithub = kwarg("g,github", "Github");
  std::optional<std::string> &varColor = kwarg("c,color", "Color");
  std::optional<std::string> &varWebsite = kwarg("w,website", "Website");

  bool &header = flag("header", "Enables document header").set_default(true);
  bool &footer = flag("footer", "Enables document footer").set_default(true);

  bool &spaced = flag("spaced", "Spaces document elements").set_default(true);
  bool &darken = flag("darken", "Darkens document elements").set_default(true);

  bool &anon = flag("anon", "Anonymize during compilation").set_default(false);
  bool &bold = flag("bold", "Bolden during compilation").set_default(false);

  bool &debug = flag("debug", "Run in debug mode").set_default(false);
  bool &interrupt = flag("interrupt", "Interrupt deep compilation").set_default(false);
};

#endif
