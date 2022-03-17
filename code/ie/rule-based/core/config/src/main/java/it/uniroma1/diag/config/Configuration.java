package it.uniroma1.diag.config;

import it.uniroma1.diag.exception.UnsetConfigurationException;
import lombok.extern.slf4j.Slf4j;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

/**
 *
 * SetupConfiguration Class This Singleton Class is responsible for loading all of
 * the initial configuration options for this service
 *
 * @author Federico Maria Scafoglieri
 */
@Slf4j
public class Configuration {

    private static Configuration instance = null;

    private Properties properties;

    /**
     * Constructor This is private so it cannot be instantiated by anyone other
     * than this class Try and load the current Config, if no config was found,
     * try to create a new one
     */
    private Configuration() {

        /*
         Prevent form the reflection api.
         */
        if (instance != null){
            throw new RuntimeException("Use getInstance() method to get the single instance of this class.");
        }

    }

    /**
     * Load the SetupConfiguration specified at fileName
     *
     * @param configFileName
     *      The path of setup configuration file
     * @return boolean
     *      did this load succeed?
     */
    private boolean loadConfig(String configFileName) {
        log.info("Create Setup Configuration");

        Properties properties = new Properties();
        InputStream input = null;

        try {
            File file = new File(configFileName);
            log.info("Loading " + file.getAbsolutePath());
            input = new FileInputStream(file);
            properties.load(input);

            if(ConfigurationValidator.isValid(properties))
                this.properties = properties;
            else
                throw new RuntimeException("Error in File " + configFileName);

        } catch(IOException e){
            log.error("Error reading default properties.");
            log.debug(e.getMessage(), e);
            throw new RuntimeException("Impossible to extract setup configuration from " + configFileName);
        } finally {
            if (input != null) {
                try {
                    input.close();
                } catch (IOException e) {
                    log.error("Error closing default properties.");
                    log.debug(e.getMessage(), e);
                    throw new RuntimeException("Impossible to extract setup configuration from " + configFileName);
                }
            }
        }
        log.info("Load Configuration Completed");
        log.debug(this.toString());

        return true;
    }

    /**
     * Get the Instance of this class There should only ever be one instance of
     * this class and other classes can use this static method to retrieve the
     * instance
     *
     * @return {@link Configuration}
     *      the stored Instance of this class
     */
    public static synchronized Configuration getInstance() {
        if (Configuration.instance == null) {
            Configuration.instance = new Configuration();
        }

        return Configuration.instance;
    }

    /**
     * Set the config file name
     *
     */
    public boolean setConfiguration(String configFileName){
        return this.loadConfig(configFileName);
    }


    /**
     * Returns the string value of the given key.
     */
    public String getProperty(String key) {
        if(this.properties == null)
            throw new UnsetConfigurationException("The Texto System is not configured yet");
        return this.properties.getProperty(key);
    }

    @Override
    public String toString() {
        return this.properties.toString();
    }

}
