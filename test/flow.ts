// test/flow.ts (pseudo)
const [admin, manu, car1, car2, oracle, pharm] = await ethers.getSigners();
const C = await ethers.getContractFactory("PharmaChain");
const c = await C.deploy(admin.address);

await c.connect(admin).grantRoleTo(ethers.id("MANUFACTURER_ROLE"), manu.address);
await c.connect(admin).grantRoleTo(ethers.id("CARRIER_ROLE"), car1.address);
await c.connect(admin).grantRoleTo(ethers.id("CARRIER_ROLE"), car2.address);
await c.connect(admin).grantRoleTo(ethers.id("ORACLE_ROLE"), oracle.address);
await c.connect(admin).grantRoleTo(ethers.id("PHARMACY_ROLE"), pharm.address);

await c.connect(manu).registerProductBirth("SH-451-B7", "ipfs://QmBirthJson...");
await c.connect(manu).createShipment("SH-451-B7", pharm.address);

await c.connect(oracle).recordTemperature("SH-451-B7", 452);
await c.connect(car1).proposeTransfer("SH-451-B7", car2.address);
await c.connect(car2).confirmPickup("SH-451-B7");
await c.connect(car2).confirmDrop("SH-451-B7");
await c.connect(oracle).recordTemperature("SH-451-B7", 901); // breach
await c.connect(pharm).markDelivered("SH-451-B7");
