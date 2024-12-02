package org.sibel.utils;

import com.opencsv.CSVReaderBuilder;
import java.io.IOException;
import java.math.BigDecimal;
import java.net.URI;
import java.net.URISyntaxException;
import java.nio.file.FileSystems;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public class EmulatorUtils {
    private static final Logger LOG = LogManager.getLogger(EmulatorUtils.class);

    private static List<BigDecimal> readDataSet(Path csvPath, String column) throws IOException {
        var dataSet = new ArrayList<BigDecimal>();
        try (var fileReader = Files.newBufferedReader(csvPath)) {
            try (var csvReader = new CSVReaderBuilder(fileReader).build()) {
                var iterator = csvReader.iterator();
                var columnNames = Arrays.asList(iterator.next());
                var columnIndex = columnNames.indexOf(column);
                while (iterator.hasNext()) {
                    var line = iterator.next();
                    dataSet.add(new BigDecimal(line[columnIndex]));
                }
            }
        }
        return dataSet;
    }

    public static List<BigDecimal> loadCsvDataSet(String csvResource, String column) {
        List<BigDecimal> dataSet;
        try {
            var csvUri = Thread.currentThread()
                    .getContextClassLoader()
                    .getResource(csvResource)
                    .toURI();

            if (csvUri.getScheme().equals("jar")) {
                final var env = new HashMap<String, String>();
                final String[] csvUriArray = csvUri.toString().split("!");
                try (var fs = FileSystems.newFileSystem(URI.create(csvUriArray[0]), env)) {
                    dataSet = readDataSet(fs.getPath(csvUriArray[1]), column);
                }
            } else {
                dataSet = readDataSet(Paths.get(csvUri), column);
            }
        } catch (URISyntaxException | IOException | NumberFormatException e) {
            LOG.error("Error initializing device, failed to load {} dataset", csvResource, e);
            throw new RuntimeException(e);
        }
        return dataSet;
    }
}
