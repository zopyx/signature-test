const crypto = require('crypto');
const fs = require('fs')


const publicKey = fs.readFileSync('public.pem', 'utf-8');

const signature = fs.readFileSync('signature.sig', 'utf-8');

const message = fs.readFileSync('payload.dat', 'utf-8');

var verifier = crypto.createVerify('sha256');

verifier.update(message);

let publicObj =crypto.createPublicKey(publicKey)

publicObj.padding = crypto.constants.RSA_PKCS1_PSS_PADDING

var ver = verifier.verify(publicObj, signature,'base64');

console.log(ver);
