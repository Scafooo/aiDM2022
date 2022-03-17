package it.uniroma1.diag.span;

import com.google.common.collect.HashBasedTable;
import com.google.common.collect.Table;
import lombok.Data;
import lombok.NonNull;
import lombok.extern.slf4j.Slf4j;

/**
 * This class represents a SpanTable
 *
 * @author Federico Maria Scafoglieri
 */
@Slf4j
@Data
public class SpanTable {

    /** The name of the SpanTable */
    private final String name;

    /** The table of the SpanTable */
    private Table<Integer, Integer, Span> table;

    /** Number of rows */
    private int row;

    /**
     * Constructor for SpanTable. TODO
     *
     * @param name the name of SpanTable
     */
    public SpanTable(@NonNull String name) {
        if (name.equals("")) {
            throw new InvalidSpanTableException("the name should not be empty");
        }

        this.name = name;
        this.table = HashBasedTable.create();
        this.row = 0;
        log.debug("Created SpanTable {}", this);
    }

    /**
     * Put the element in the specified collection to the SpanTable.
     *
     * @param spanTuple
     */
    public void put(SpanTuple spanTuple) {

        int row = (this.size()/spanTuple.getCollection().size());
        int column = 0;
        for (Span span : spanTuple.getCollection()) {
            this.table.put(row, column, span);
            log.debug("Adding SpanTuple {} in {}-{}", spanTuple, row, column);
            column++;
        }
    }

    /**
     * Put all the elements in the specified table to the this SpanTable.
     *
     * @param table
     */
    public void putAll(Table<Integer, Integer, Span> table) {
        this.table.putAll(table);
    }

    /**
     * Return the size of the table. Ex in compact way: {0={0={0:1,D1}, 1={0:3,D2}}}
     * the size is equal to 2
     *
     * @return an Integer representing the size of the SpanTable (the header is excluded)
     */
    public int size() {
        return this.table.size();
    }

    /**
     * Print the SpanTable as a Table like the SQL shell representation
     */
    public void printTable(){
        System.out.println(this.table.columnKeySet());
        for (Table.Cell<Integer, Integer, Span> cell: table.cellSet()){
            System.out.println(cell.getRowKey()+" "+" "+cell.getValue());
        }
    }
}
