//During the test the env variable is set to test
process.env.NODE_ENV = 'test';

//Require the dev-dependencies
let chai = require('chai');
let chaiHttp = require('chai-http');
let server = require('../bin/www');
let should = chai.should();


chai.use(chaiHttp);
/* Our parent block */
describe('config', () => {
    /*
    beforeEach((done) => { //Before each test we empty the database
        Book.remove({}, (err) => { 
           done();           
        });        
    });
    */
    /*
     * Test the /GET config route
     */
    describe('/GET config ', () => {
        it('it should GET config', (done) => {
            chai.request(server)
                .get('/config')
                .end((err, res) => {
                    res.should.have.status(200);
                    console.log(res.body);
                    //res.body.should.be.eql(checkObj);
                    //res.body.length.should.be.eql(0);
                    done();
                });
        });
    });
    /*
     * Test the /GET config/pc route
     */
    describe('/GET config/pc ', () => {
        it('it should GET config pc', (done) => {
            chai.request(server)
                .get('/config/pc')
                .end((err, res) => {
                    res.should.have.status(200);
                    //should evaluate the config    
                    //res.body.should.be.eql(checkObj);
                    //res.body.length.should.be.eql(0);
                    done();
                });
        });
    });
    /*
     * Test the /GET config/ocr route
     */
    describe('/GET config/ocr ', () => {
        it('it should GET config ocr', (done) => {
            chai.request(server)
                .get('/config/ocr')
                .end((err, res) => {
                    res.should.have.status(200);
                    // should evaluate the config    
                    //console.log(res.body);
                    //res.body.should.be.eql(checkObj);
                    //res.body.length.should.be.eql(0);
                    done();
                });
        });
    });

});