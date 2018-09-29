
Author : FOSS INFOTECH PVT LTD

Module : SUBCONTRACT\_MANUFACTURING

Version : 11.0

<h2>SUBCONTRACT</h2>

<p>ODOO 11 Module for Subcontracting based on Manufacturing.</p>

<p><b>Subcontract Location Creation</b>:</p>
<img src="static/description/S1.png">

<p><b>Location Assigning for Vendor</b>:</p>
<img src="static/description/S2.png">

<p><b>Step 1</b>: Create Manufacturing Order :</p>
<img src="static/description/S7.png">

<p><b>Step 2</b>: Check the Stock Availability :</p>
<img src="static/description/S8.png">

<p><b>Step 3</b>: Manufacturing the product by clicking on Produce button :</p>
<img src="static/description/S9.png">

<p><b>Step 4</b>: Quantity on Hand for the product that is to be manufactured :</p>
<img src="static/description/S3.png">

<p><b>Step 5</b>: If there is no stock in Subcontract location then while clicking on Record Production button we would get the follwing error :</p>
<img src="static/description/S10.png">

<p><b>Step 6</b>: Increase the stock of the raw materials in Subcontract location by using the delivery order. In Delivery a subcontract field will be present where we would check it and select the BOM material for which the stock is to be added and click on Update button to get the raw materials automatically populated and also choose the destination location where the stock has to be increased :</p>
<img src="static/description/S15.png">

<p><b>Step 7</b>: Quantity on Hand for the raw materials in subcontract location :</p>  
<img src="static/description/S16.png">

<p><b>Step 8</b>: After increasing the stock, we can produce the products either fully or partially :</p>  
<img src="static/description/S17.png">

<p><b>Step 9</b>: While producing the product, automatically Purchase order will be created :</p>  
<img src="static/description/S18.png">

<p><b>Step 10</b>: Confirm the Purchase order to create Shipments :</p>  
<img src="static/description/S19.png">

<p><b>Step 11</b>: Specify the done quantity in order to process the shipments else the following error will be populated :</p>  
<img src="static/description/S21.png">

<p><b>Step 12</b>: Shipments cannot be validated until Post inventory button is clicked in Manufacturing order as stock movement will be done only after that process. Please find the following error for the same :</p>  
<img src="static/description/S23.png">

<p><b>Step 13</b>: Only the produced products can be processed in incoming shipments else the following error will be populated :</p>  
<img src="static/description/S31.png">

<p><b>Step 14</b>: For partial shipping of the products Create Backorder and No Backorder button can be used :</p>  
<img src="static/description/S26.png">

<p><b>Step 15</b>: Incoming Shipments (Receipts) of the Backorders.</p>  
<img src="static/description/S35.png">

<p><b>Step 16</b>: Clicking on the Post inventory button, stock movements will be done :</p>  
<img src="static/description/S33.png">

<p><b>Step 17</b>: Quantity on Hand for the product that is manufactured :</p>  
<img src="static/description/S37.png">

<p><b>Step 18</b>: (Products -> Product Moves) Corresponding Product Moves for Manufactured product is displayed below :</p>
<img src="static/description/S39.png">

<p><b>Step 19</b>: Quantity on Hand for the raw materials in subcontract location after production :</p>  
<img src="static/description/S38.png">

<p><b>Step 20</b>: Once after the completion of all the shipments, automatically the Manufacturing order will be moved to Done state :</p>  
<img src="static/description/S36.png">
