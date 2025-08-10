<h1 style="text-align: center;"><em>Care Simulator</em></h1>

<!-- <p align="center">
  <img src="frontend/src/assets/genie.png" alt="Description" width="300"/>
</p> -->

# Installation Manual

**Clone the Repository:**

  * Using SSH:  

    ```bash
    git clone git@github.com:infinity-sandbox/care-sim.git
    ```
  * Using HTTPS:  

    ```bash
    git clone https://github.com/infinity-sandbox/care-sim.git
    ```

**Navigate into the `care-sim` Directory:**

  ```bash
  cd care-sim
  ```

## For macOS & linux

**Grant Execution Permissions:**

  * Give execution rights to the installation shell script:

    ```bash
    chmod 777 initializeSignals.sh
    ```

**Run the Installation Script:**

  * Start Docker Dameon & Execute the installation script to set up the system:

    ```bash
    ./initializeSignals.sh
    ```

### Binaries

**Run the Documentation:**

  * Grant execution permissions and run the documentation script:

    ```bash
    chmod 777 backendDocs.sh
    ./backendDocs.sh
    ```

**Get the Binary Stable Build for Shipment:**

  * Grant execution permissions and run the script to generate the binaries:

    ```bash
    chmod 777 convertToBinaries.sh
    ./convertToBinaries.sh
    ```

  * After running the script, you can find the binary build for  macos & linux in `bin/arm.zip`

## For windows

**Run the Installation Batch Script:**

  * Start Docker Dameon & Execute the installation batch script to set up the system:

    ```bash
    initializeSignals.bat
    ```

### Binaries

**Get the Binary Stable Build for Shipment:**

  * Generate the binaries by running the batch file:

    ```bash
    convertToBinaries.bat
    ```
      
  * After running the script, you can find the binary build for  Windows in `bin/win.zip`

**Run the Documentation Script:**

  * Run the documentation batch file:

    ```bash
    backendDocs.bat
    ```
  