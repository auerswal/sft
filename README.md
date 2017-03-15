# Single File Tools (SFT)

This repository collects a couple of simple utilities written in different
languages for varying use cases. The single common factor is an implementation
comprising just one file. These single file tools are usually written in an
interpreted (or scripting) language.

## License

All tools contain licensing information in the file. In general, every tool
is published under a free software license. Additionally, this collection
is available under the
[GNU General Public License](https://www.gnu.org/licenses/gpl.html)
version 3 or later.

## The Tools

Some of the single file tools have been published already using a dedicated
web page. In that case a link to the web page is provided.

* `checkzips` - check ZIP files for errors
* `create_ipv6_ULA_global_prefix_random.sh` - create a random global prefix for IPv6 ULA addresses using `/dev/random`
* `create_ipv6_ULA_global_prefix_rfc4193.sh` - create a random global prefix for
IPv6 ULA addresses using a deterministic algorithm based on [RFC 4193 section 3.2.2](https://tools.ietf.org/html/rfc4193#section-3.2.2)
* `dvdmovie` - play the main movie from a video DVD with [MPlayer](http://www.mplayerhq.hu/) ([web page](https://www.unix-ag.uni-kl.de/~auerswal/dvdmovie/))
* `ext_ip` - print externally visible IPv4 and IPv6 addresses
* `ffdl` - simple download helper for Firefox
* `foreachpam` - invoke program for each image in a PAM stream ([web page](https://www.unix-ag.uni-kl.de/~auerswal/netpbm/index.html))
* `foreachpnm` - invoke program for each image in a PNM stream ([web page](https://www.unix-ag.uni-kl.de/~auerswal/netpbm/index.html))
* `hide_passwords_enterasys.sed` - mask passwords in Enterasys (now Extreme) EOS configuration (available on my [Notes on Enterasys Networks Equipment](https://www.unix-ag.uni-kl.de/~auerswal/enterasys/) web page)
* `ipcalc` - simple replacement for [ipcalc](http://jodies.de/ipcalc)
* `macfmt` - convert MAC address formats ([web page](https://www.unix-ag.uni-kl.de/~auerswal/macfmt/))
* `net2ips` - print host addresses of an IPv4 network (uses ipcalc)
* `netio-kshell-dos` - demonstrate TCP session cleanup bug ([web page](https://www.unix-ag.uni-kl.de/~auerswal/netio-kshell-bug/))
* `nfoview` - view NFO files on GNU/Linux
* `ping_scan` - ping many hosts at once ([web page](https://www.unix-ag.uni-kl.de/~auerswal/ping_scan/))
* `ping_wrapper` - wrapper around iputils ping for use with `ping_scan` ([web page](https://www.unix-ag.uni-kl.de/~auerswal/ping_scan/))
* `pnmcat-stream` - wrapper for [pnmcat](http://netpbm.sourceforge.net/doc/pnmcat.html) to work with image streams ([web page](https://www.unix-ag.uni-kl.de/~auerswal/netpbm/index.html))
* `priv_pass.py` - Calculate ROMMON priv password for (some) Cisco routers
* `rfc-reader` - read IETF RFCs on GNU/Linux ([web page](https://www.unix-ag.uni-kl.de/~auerswal/rfc-reader/))
* `total_video_duration` - print total run time of given video files (uses `ffprobe` from [FFmpeg](https://ffmpeg.org/))
