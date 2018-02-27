import os
import re

ERRORINDICATOR = "error: This func has return reference, but the inputs are immutable"
WARNINDICATOR = "warning: This func has return reference, but the inputs are immutable"
SUMMERARYINDICATOR = "`mylint` finished,\n"

summary_pattern = re.compile("")

class SingleLintMsg:
    def __init__(self, lines):
        """
        An example of line:
            error: This func has return reference, but the inputs are immutable
                --> slice.rs:1386:5
                 |
            1386 |       pub fn into_slice(self) -> &'a mut [T] {
                 |  _____^ starting here...
            1387 | |         make_mut_slice!(self.ptr, self.end)
            1388 | |     }
                 | |_____^ ...ending here
                 |
                 = note: #[deny(test_lint)] implied by #[deny(warnings)]
                 = help: for further information visit https://github.com/Manishearth/rust-clippy/wiki#test_lint
        """
        # self.contents = ""
        self.error_location = lines[2].split("-->")[-1][1:]
        self.error_info = lines[4]
        self.error_body = ""
        for line in lines[2:10]:
            self.error_body += line
        # tmp_start = lines[4].find("fn")
        # tmp_end = lines[4][tmp_start:].find("{")
        # self.error_func_proto = lines[4][tmp_start: tmp_start + tmp_end]
        self.error_func_name = lines[0]


    def __str__(self):
        # return self.error_func_name + self.error_location + self.error_info
        return self.error_func_name + self.error_body

    def get(self):
        return (self.error_location, self.error_info)

    def to_asciidoc(self, option = True):
        #FIXME
        if option is True:
            return "\n* " + self.error_func_name + "+\n```\n" \
                    + self.error_location \
                    + self.error_body \
                    + "```\n"
        else:
            return "\n* " + self.error_func_name + "\n```\n" \
                   + self.error_location \
                   + self.error_body \
                   + "```\n"
    
    def to_markdown(self):
        return self.to_asciidoc(False)
        
        

class LintResutSummary:
    """
    Example Summary Words:
    `mylint` finished,
                 7645 functions in total,
                 157 have mut return refererance,
                 11 are with immutable inputs,
                 after `mylint` pass.
    """
    def __init__(self, lines):
        self.contents = lines
        self.func_count = int(lines[1].split()[0])
        self.mut_rtn_count = int(lines[2].split()[0])
        self.imu_mut_count = int(lines[3].split()[0])

    def __str__(self):
        return str(self.func_count) + " functions.\n" \
                + str(self.mut_rtn_count) + " mut returns.\n" \
                + str(self.imu_mut_count) + " imut input and mut returns.\n"
        #return self.contents
    def to_asciidoc(self, option = True):
        #FIXME
        if option is True:
            return  "The summary of the mylint results: \n" \
                    + str(self.func_count) + " functions.\n" \
                    + str(self.mut_rtn_count) + " mut returns.\n" \
                    + "**" + str(self.imu_mut_count) + " imut input and mut returns.**\n\n"
        else:
            return  "The summary of the mylint results: \n\n\t" \
                    + str(self.func_count) + " functions.\n\n\t" \
                    + str(self.mut_rtn_count) + " mut returns.\n\n\t" \
                    + "**" + str(self.imu_mut_count) + " imut input and mut returns.**\n\n"            

    def to_markdown(self):
        return self.to_asciidoc(False)

    def get_results(self):
        return (self.func_count, self.mut_rtn_count, self.imu_mut_count)

class CompileFailureMsg:
    def __init__(self, lines):
        self.error_msg = ""
        for line in lines:
            self.error_msg += line

    def to_asciidoc(self, option = True):
        #FIXME
        if option:
            if len(self.error_msg) > 10:
                return "+\n" + "```\n"+ self.error_msg[-10:] + "```\n"
            else:
                return "+\n" + "```\n"+ self.error_msg + "```\n"
        else:
            if len(self.error_msg) > 10:
                return "\n" + "```\n"+ self.error_msg[-10:] + "```\n"
            else:
                return "\n" + "```\n"+ self.error_msg + "```\n"

    def to_markdown(self):
        return self.to_asciidoc(False)

    def __str__(self):
        return self.error_msg

    def get_results(self):
        return None

class Mylintlog:
    def __init__(self, contents, git_repo = ""):
        """
        input:
            contents should be an array of strings
        """
        self.logcontents = contents
        self.count = 0
        self.func_count = 0
        self.errors = []
        self.summary = None
        self.process()

    def process(self):
        #:wprint self.logcontents
        """ process the string read from the pipe, analyze it, and get the results:

        """
        self.errors = []
        length_fo_log = len(self.logcontents)
        
        for i in range(0,length_fo_log):
            # if "error, error: This func has return reference, but the inputs are immutable
            if ERRORINDICATOR in self.logcontents[i]:
                SLM_new = SingleLintMsg(self.logcontents[i-1:i+11])
                self.errors.append(SLM_new)
            if WARNINDICATOR in self.logcontents[i]:
                SLM_new = SingleLintMsg(self.logcontents[i-1:i+11])
                self.errors.append(SLM_new)
            if SUMMERARYINDICATOR in self.logcontents[i]:
                LRS_summary = LintResutSummary(self.logcontents[i:i+4])
                self.summary = LRS_summary
        if self.summary is None:
            print("SUMMERARYINDICATOR not found")
            self.summary = CompileFailureMsg(self.logcontents)

    def to_file(self, filepath):
        try:
            fp = open(filepath, "w");
            for line in self.logcontents:
                fp.write(line)
            fp.close()
        except Exception as e:
            print("Failed to write logs: ".format(str(e)))

    def to_asciidoc(self, summary_filepth = "mylint.adoc"):
        #FIXME
        try:
            fp = open(summary_filepth,"w")
            fp.write("= MyLintLog\n\n")
            # Write summary
            if self.summary is not None:
                fp.write(self.summary.to_asciidoc())
            #
            fp.write("== List of the imu_to_mut functions\n\n")
            for e in self.errors:
                fp.write(e.to_asciidoc())
            fp.close()
        except Exception as e:
            print("In to_asciidoc of Mylintlog, Failed to write log to asciidoc".format(str(e)))
    
    def to_markdown(self, summary_filepth = "mylint.md"):
        try:
            fp = open(summary_filepth,"w")
            fp.write("# MyLintLog\n\n")
            # Write summary
            if self.summary is not None:
                fp.write(self.summary.to_markdown())
            #
            fp.write("## List of the imu_to_mut functions\n\n")
            for e in self.errors:
                fp.write(e.to_markdown())
            fp.close()
        except Exception as e:
            print("In to_asciidoc of Mylintlog, Failed to write log to asciidoc".format(str(e)))

    def get_asciidoc_str(self):
        #FIXME
        if self.summary is not None:
            output_str = ""
            output_str += self.summary.to_asciidoc()
            for e in self.errors:
                output_str += e.to_asciidoc()
                output_str += "\n"
            return output_str
        return "Error Occured!"

    def get_count(self):
        return self.count

    def get_funccount(self):
        return self.func_count

    def get_summary(self):
        return self.summary

    def __repr__(self):
        return "Mylintlog()"

    def __str__(self):
        return ""


def save_log(contents, logfile):
    fp = open(logfile, "w")
    for line in contents:
        fp.write(line)
    fp.close()

def print_log(contents):
    for line in contents:
        print(line)


def logger_load_log(logfile):
    if os.path.exists(logfile):
        fp = open(logfile)
        contents = fp.readlines()
        fp.close()
        return contents
    return []


def process_newnutlint_log(contents):
    """
    Input:
        contents, an array of log lines
    """
    summary = []
    line_num = len(contents)
    for i in range(0, line_num):
        if contents[i] == SUMMERARYINDICATOR:
            # print("SUMMERARYINDICATOR found")
            for j in [1, 2, 3, 4]:
                tmp = contents[i+j]
                try:
                    summary.append(int(tmp.split()[0]))
                    # print("\t", tmp,summary)
                except Exception as e:
                    print("Exception in process_newmutling_log: ", str(e))
                    return None
    if summary == []:
        return None
    return tuple(summary)

def process_mutlint_logger(contents, srcdir = "."):
    try:
        mlog = Mylintlog(contents)
    except Exception as e:
        print("Exception In process_mutlint_log:\n", str(e))
        return
    if mlog == None:
        return None    
    mlog.process()
    logfile = os.path.join(srcdir,"buildlog.md") # Save log file
    mlog.to_markdown(logfile)
    return mlog.get_summary().get_results()

FAILCOMPILE = "error: Could not compile"
CARGOFAIL = "error: failed to parse manifest"

def is_build_success(contents):
    for i in contents:
        if i.startswith(FAILCOMPILE):
            return False
        if i.startswith(CARGOFAIL):
            print("Error in Cargo.toml: ", CARGOFAIL)
            return False
    return True

def test_main():
    fp = open("../tests/newmut.log")
    contents = fp.readlines()
    fp.close()
    print(process_newnutlint_log(contents))
    #print(process_mutlint_logger(contents))
    # mlog = Mylintlog(contents)
    # mlog.process()
    # mlog.to_asciidoc()
    # mlog.to_markdown()
    # x = mlog.get_asciidoc_str()


if __name__ == "__main__":
    test_main()
