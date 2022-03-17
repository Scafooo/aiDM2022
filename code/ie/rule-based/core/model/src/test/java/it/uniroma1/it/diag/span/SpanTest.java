package it.uniroma1.it.diag.span;

import it.uniroma1.diag.document.Document;
import it.uniroma1.diag.span.Span;
import org.junit.Test;

import static org.junit.Assert.assertEquals;

/** Unit test for Span */
public class SpanTest {

    @Test
    public void spanGetText() {
        Document document = new Document("Rome Milan");
        Span span = new Span(0, 4, document);
        assertEquals(span.getText(), "Rome");
    }
}
