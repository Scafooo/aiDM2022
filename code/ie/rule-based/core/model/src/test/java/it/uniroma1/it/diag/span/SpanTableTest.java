package it.uniroma1.it.diag.span;

import it.uniroma1.diag.document.Document;
import it.uniroma1.diag.span.Span;
import it.uniroma1.diag.span.SpanTable;
import it.uniroma1.diag.span.SpanTuple;
import org.junit.Test;

import static org.junit.Assert.assertTrue;

public class SpanTableTest {

    @Test
    public void spanGetTable() {
        Document document1 = new Document("Rome");
        Span span1 = new Span(0, 4, document1);

        Document document2 = new Document("Milan");
        Span span2 = new Span(0, 4, document2);

        SpanTuple spanTuple1 = new SpanTuple();
        spanTuple1.add(span1);
        spanTuple1.add(span1);
        spanTuple1.add(span1);

        SpanTuple spanTuple2 = new SpanTuple();
        spanTuple2.add(span2);
        spanTuple2.add(span2);
        spanTuple2.add(span2);

        SpanTable spanTable = new SpanTable("TestTable");
        spanTable.put(spanTuple1);
        spanTable.put(spanTuple2);

        spanTable.printTable();

        assertTrue(true);


    }
}
