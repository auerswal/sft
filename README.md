# Single File Tools (SFT)

This repository collects a couple of simple utilities written in different
languages for varying use cases. The single common factor is an implementation
comprising just one file. These single file tools are usually written in an
interpreted (or scripting) language.

All single file tools are intended to be usable without installation. I
usually check out this repository on every machine I work with. If one of
the tools needs to be started from a specific directory that is a bug.

## License

All tools contain licensing information in the file. In general, every tool
is published under a free software license. Additionally, this collection
is available under the
[GNU General Public License](https://www.gnu.org/licenses/gpl.html)
version 3 or later.

## The Tools

Some of the single file tools have been published already using a dedicated
web page. In that case a link to the web page is provided.

### Documentation

If a dedicated web page for a single file tool exists, it contains
documentation for the specific tool. Additionally, since all tools
are comprised of a single file, their documentation, as far as it
exists, is part of the program itself.

All tools are scripts for some interpreter, thus they can be viewed with
any text viewer, e.g., a pager or an editor. Usually the documentation
is included as a comment after the copyright statement.

Sometimes the tool supports a `-h` option to show help.

Sometimes, if the tool is not a filter, it prints out a help screen if
called without any operands (neither options nor arguments).

Some of the tools complement each other.  E.g., `ping_wrapper` allows
using `ping_scan` on GNU/Linux, and `net2ips` uses `ipcalc`, either
https://jodies.de/ipcalc or the `ipcalc` script from this collection.

### List of Single File Tools

* `archive_url` - archive the given URLs in the
  [Wayback Machine](https://web.archive.org/), unless they are already
  archived there
* `capture.sh` - capture traffic on an interface for a given duration with
  `tcpdump`
* `checkzips` - check ZIP files for errors
* `create_ipv6_ULA_global_prefix_random.sh` - create a random global prefix
  for IPv6 ULA addresses using `/dev/random`
* `create_ipv6_ULA_global_prefix_rfc4193.sh` - create a pseudo random global
  prefix for IPv6 ULA addresses using a deterministic algorithm based on
  [RFC 4193 section 3.2.2](https://datatracker.ietf.org/doc/html/rfc4193#section-3.2.2)
* `dvdmovie` - play the main movie from a video DVD with
  [MPlayer](http://www.mplayerhq.hu/)
  ([web page](https://www.unix-ag.uni-kl.de/~auerswal/dvdmovie/))
* `enclosing-section` - print all enclosing sections containing a line
  matching a regular expression (inspired by the Huawei VRP output modifier
  *section include*; see my more featureful
  [Go implementation of section](https://www.unix-ag.uni-kl.de/~auerswal/section/index.html)
  as well)
* `ensure_bom_crlf` - Prepare a UTF-8 encoded POSIX text file for use on
  Windows by ensuring it starts with the UTF-8 encoded unicode code point
  U+FEFF "zero-width no-break space" (the old UCS-2 byte order mark (BOM)),
  and uses the CR LF (`"\r\n"`) end-of-line character sequence
* `ext_ip` - print externally visible IPv4 and IPv6 addresses
* `ffdl` - simple download helper for Firefox
* `foreachpam` - invoke program for each image in a PAM stream
   ([web page](https://www.unix-ag.uni-kl.de/~auerswal/netpbm/index.html))
* `foreachpnm` - invoke program for each image in a PNM stream
  ([web page](https://www.unix-ag.uni-kl.de/~auerswal/netpbm/index.html))
* `hide_passwords_enterasys.sed` - mask passwords in Enterasys (now Extreme)
  EOS configuration
  (available on my
  [Notes on Enterasys Networks Equipment](https://www.unix-ag.uni-kl.de/~auerswal/enterasys/#hide_passwords)
  web page)
* `ifstats` - print interface statistics (counters) on Linux (uses *sysfs*)
* `interface_status` - query interface status of network devices via SNMP
* `intf_names` - print interface names on Linux (uses *sysfs*)
* `ipcalc` - simple replacement for the *jodies.de*
   [IP Calculator](https://jodies.de/ipcalc) of the same name
* `ipenum.py` - enumerate IPv4 and IPv6 addresses from the given ranges;
  ranges can be specified via start and end addresses, or in CIDR notation
  (implemented in Python 3 based on the Python standard library (*stdlib*)
  modules `ipaddress` and `re`)
* `isascii` - check if all input bytes contain 7-bit ASCII values
* `macfmt` - convert MAC address formats
  ([web page](https://www.unix-ag.uni-kl.de/~auerswal/macfmt/))
* `macfmt.py` - alternative to the above `macfmt`, implemented in Python
  instead of Awk (mentioned on the `macfmt`
  [web page](https://www.unix-ag.uni-kl.de/~auerswal/macfmt/))
* `net2ips` - print host addresses of an IPv4 network (uses `ipcalc`)
* `net2ips.py` - print addresses of IPv4 and IPv6 networks given in CIDR
   notation, implemented in Python 3 based on the Python standard library
   (*stdlib*) module `ipaddress`
* `netio-kshell-dos` - demonstrate TCP session cleanup bug
  ([web page](https://www.unix-ag.uni-kl.de/~auerswal/netio-kshell-bug/))
* `nfoview` - view NFO files on GNU/Linux
* `ping_scan` - ping many hosts at once
  ([web page](https://www.unix-ag.uni-kl.de/~auerswal/ping_scan/))
* `ping_wrapper` - wrapper around iputils `ping` for use with `ping_scan`
  ([web page](https://www.unix-ag.uni-kl.de/~auerswal/ping_scan/))
* `pmtud` - Path MTU discovery to given IP / HOSTNAME using ICMP Echo Request
  probes
* `pnmcat-stream` - wrapper for
  [pnmcat](http://netpbm.sourceforge.net/doc/pnmcat.html)
  to work with image streams
  ([web page](https://www.unix-ag.uni-kl.de/~auerswal/netpbm/index.html))
* `priv_pass.py` - calculate ROMMON priv password for (some) Cisco routers
* `renumber` - renumber a set of discontiguously numbered files
* `rfc-reader` - read IETF RFCs and I-Ds on GNU/Linux
  ([web page](https://www.unix-ag.uni-kl.de/~auerswal/rfc-reader/))
* `section` - print all lines matching a regular expression, and the following
  indented section (inspired by the Cisco IOS output modifier of the same name)
  (see my more featureful
  [Go implementation of section](https://www.unix-ag.uni-kl.de/~auerswal/section/index.html)
  as well)
* `section.pl` - Perl version of the above `section` script, for use on systems
  without Awk, but Perl, such as some Cisco IOS XR versions (see my more
  featureful
  [Go implementation of section](https://www.unix-ag.uni-kl.de/~auerswal/section/index.html)
  as well)
* `section.py` - Python version of the above `section` script, for use on
  systems without Awk or Perl, but Python (see my more featureful
  [Go implementation of section](https://www.unix-ag.uni-kl.de/~auerswal/section/index.html)
  as well)
* `slatel` - strip leading and trailing empty lines
* `thotp.py` - compute one-time passwords using the
  HOTP ([RFC 4226](https://www.rfc-editor.org/rfc/rfc4226.html)) or
  TOTP ([RFC 6238](https://www.rfc-editor.org/rfc/rfc6238.html)) algorithms
* `top-level-section` - print all top-level sections containing a line matching
  a regular expression (inspired by the Arista EOS output modifier *section*;
  see my more featureful
  [Go implementation of section](https://www.unix-ag.uni-kl.de/~auerswal/section/index.html)
  as well)
* `total_video_duration` - print total run time of given video files
  (uses `ffprobe` from [FFmpeg](https://ffmpeg.org/))
* `vevent_dump` - print a somewhat readable version of the essential information
  inside an iCalendar (`.ics`) file to STDOUT (best effort only, not even trying
  to parse the format...)
* `vrp_output_to_yaml.awk` - convert log from command execution on Huawei VRP
  device into YAML encoded list of dictionaries each comprising an executed
  command and its output

## Junkcode

If you do not find what you are looking for in this repository, you might
find example code licensed under the GNU Public License version 3 or later
in my [junkcode](https://github.com/auerswal/junkcode/) repository.

## Homepage

For more of my work you can visit my
[homepage](https://www.unix-ag.uni-kl.de/~auerswal/) at the
[Unix-AG](https://www.unix-ag.uni-kl.de/) of the
[TU Kaiserslautern](https://www.uni-kl.de/).
