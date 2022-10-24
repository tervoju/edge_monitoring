var express = require('express');
var router = express.Router();
const fs = require('fs');
const bodyParser = require('body-parser');
const uploadFile = require("../middleware/upload");


/** 
 * @swagger
 *  /
 *    get:
 *      summary: Get intro page
 *      tags: [intro]
 *      requestBody:
 *        required: false
 *      responses:
 *        200:
 *          description: Success
*/
router.get('/', function (req, res, next) {
  res.render('index', { title: 'Edge config server' });
});

/*ocr camera configuration file */
/** 
 * @swagger
 *  /config/ocr
 *    get:
 *      summary: Get ocr configuration
 *      tags: OCR
 *      requestBody:
 *        required: false
 *      responses:
 *        200:
 *          description: Success
*/
router.get('/config/ocr', async (req, res) => {
  const configPath = __basedir + "/configs/ocr.yaml";
  res.download(configPath, "ocr.yaml", (err) => {
    if (err) {
      res.status(500).send({
        message: "Could not download the ocr config file. " + err,
      });
    }
  });
});

/*point clouds configuration file */
router.get('/config/pc', async (req, res) => {
  const configPath = __basedir + "/configs/pc.yaml";
  res.download(configPath, "pc.yaml", (err) => {
    if (err) {
      res.status(500).send({
        message: "Could not download the pointcloud config file. " + err,
      });
    }
  });
});

/* get configs */
router.get('/configs', async (req, res) => {
  const configPath = __basedir + "/configs";
  //passsing configPath and callback function
  fs.readdir(configPath, function (err, files) {
    //handling error
    if (err) {
      console.log('Unable to scan directory: ' + err);
      res.status(500).send({
        message: "Could not find the config files. " + err,
      });
    }
    //listing all files using forEach
    configurations = [];
    files.forEach(function (file) {
      if (file != "prev") // ignoring the previous configs
        configurations.push(file);
      console.log(file);
    });
    res.status(200).send({
      configurations
    });
  });
});

/* get previous configs */
router.get('/prev', async (req, res) => {
  const configPath = __basedir + "/configs/prev";
  //passsing configPath and callback function
  fs.readdir(configPath, function (err, files) {
    //handling error
    if (err) {
      console.log('Unable to scan directory: ' + err);
      res.status(500).send({
        message: "Could not find the config files. " + err,
      });
    }
    //listing all files using forEach
    configurations = [];
    files.forEach(function (file) {
      if (file != "prev") // ignoring the previous configs
        configurations.push(file);
      console.log(file);
    });
    res.status(200).send({
      configurations
    });
  });
});


/* pc - new config. */
router.post('/config/pc', async (req, res) => {
  try {
    await uploadFile(req, res);

    if (req.file == undefined) {
      return res.status(400).send({ message: "Upload a pc file please!" });
    }
    if (req.file.originalname != "pc.yaml")
    {
      return res.status(500).send({
        message: "Wrong file name",
      });
    }

    const configFileName = "pc.yaml";
    const configPath = __basedir + "/configs/";
    const configFilePath = configPath + configFileName;

    const copyFilePath = configPath + 'prev/' +  configFileName;
    // Copying config to a prev folder
    fs.copyFile(configFilePath, copyFilePath, (err) => {
      if (err) {
        console.log("Copy file failed: An Error Occured:", err);
      }
      else {
        // Printing the current file name after executing the function
        console.log("File Contents of async_copied_file:",
          fs.readFileSync(copyFilePath, "utf8"));
      }
    })
    res.status(200).send({
      message: "The following file was uploaded successfully: " + req.file.originalname,
    });
  }
  catch (err) {
    if (err.code == "LIMIT_FILE_SIZE") {
      return res.status(500).send({
        message: "File larger than 2MB cannot be uploaded!",
      });
    }
    res.status(500).send({
      //${req.file.originalname}.
      message: `Unable to upload the file:  ${err}`,
    });
  }
});

/* ocr - new config. */
router.post('/config/ocr', async (req, res) => {
  try {
    await uploadFile(req, res);

    if (req.file == undefined) {
      return res.status(400).send({ message: "Upload a file please!" });
    }
    if (req.file.originalname != "ocr.yaml")
    {
      return res.status(500).send({
        message: "Wrong file name",
      });
    }

    const confFileName = "ocr.yaml"
    const configPath = __basedir + "/configs/";
    const configFilePath = configPath + confFileName;
    const copyFilePath = configPath + 'prev/' + confFileName;
    // Copying sample_file.txt to a different name
    fs.copyFile(configFilePath, copyFilePath, (err) => {
      if (err) {
        console.log("Copy file failed: An Error Occured:", err);
      }
      else {
        // Printing the current file name after executing the function
        console.log("File Contents of async_copied_file:",
          fs.readFileSync(copyFilePath, "utf8"));
      }
    })
    res.status(200).send({
      message: "The following file was uploaded successfully: " + req.file.originalname,
    });
  }
  catch (err) {
    if (err.code == "LIMIT_FILE_SIZE") {
      return res.status(500).send({
        message: "File larger than 2MB cannot be uploaded!",
      });
    }
    res.status(500).send({
      //${req.file.originalname}.
      message: `Unable to upload the file:  ${err}`,
    });
  }
});

/* any new config. */
router.post('/config/:confName', async (req, res) => {
  try {
    await uploadFile(req, res);

    if (req.file == undefined) {
      return res.status(400).send({ message: "Upload a configuration file please!" });
    }
    /* check if config is same name */
    const configFileName = req.params.confName;
    attachedFileName = req.file.filename.split('.')[0];
    if (attachedFileName != configFileName) {
      return res.status(500).send({
        message: "Wrong filename: " + configFileName + " vs " + attachedFileName,
      })
    }

    today = new Date();
    const configPath = __basedir + "/configs/";
    const configFilePath = configPath + configFileName;
    const copyFilePath = configPath + 'prev/' + configFileName;
    // Copying config to a prev folder
    fs.copyFile(configFilePath, copyFilePath, (err) => {
      if (err) {
        console.log("Copy file failed: An Error Occured:", err);
      }
      else {
        // Printing the current file name after executing the function
        console.log("File Contents of async_copied_file:",
          fs.readFileSync(copyFilePath, "utf8"));
      }
    })
    res.status(200).send({
      message: "The following file was uploaded successfully: " + req.file.originalname,
    });
  }
  catch (err) {
    if (err.code == "LIMIT_FILE_SIZE") {
      return res.status(500).send({
        message: "File larger than 2MB cannot be uploaded!",
      });
    }
    res.status(500).send({
      //${req.file.originalname}.
      message: `Unable to upload the file:  ${err}`,
    });
  }

});

module.exports = router;
