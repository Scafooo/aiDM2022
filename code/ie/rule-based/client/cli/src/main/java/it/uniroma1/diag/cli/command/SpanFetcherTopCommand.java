package it.uniroma1.diag.cli.command;

import it.uniroma1.diag.cli.SpanFetcherCommand;
import org.jline.reader.LineReader;
import org.jline.reader.impl.LineReaderImpl;
import picocli.CommandLine;

import java.io.PrintWriter;

@CommandLine.Command(
    name = "",
    description = "Span Fetcher Command Line",
    footer = {"", "Press Ctl-D to exit."},
    subcommands = {
            SpanFetcherCreate.class,
            SpanFetcherShow.class,
            SpanFetcherUseSpanDatabase.class,
            SpanFetcherDescribeSpanTable.class,
            SpanFetcherDrop.class})
public class SpanFetcherTopCommand implements SpanFetcherCommand {
    private LineReaderImpl reader;
    private PrintWriter out;

    public void setReader(LineReader reader){
        this.reader = (LineReaderImpl)reader;
        out = reader.getTerminal().writer();
    }

    public PrintWriter getOut() {
        return out;
    }

    public void run() {
        out.println(new CommandLine(this).getUsageMessage());
    }

}
