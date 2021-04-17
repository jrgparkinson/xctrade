
import {Link} from 'react-router-dom';
import TextField from '@material-ui/core/TextField';
import TableCell from '@material-ui/core/TableCell';
import TableRow from '@material-ui/core/TableRow';

export default function AuctionAthleteBid({share, bid, updateBid}) {

    // console.log("Render auction athlete bid with " + JSON.stringify(bid));

    if (bid === undefined) {
        bid = {volume: 0.0, athlete: share.athlete.pk,
            price_per_volume: 0.0};
    }

    const volumeChanged = (e) => {
        console.log(e.target.value);
        // bid.volume = Number(e.target.value).toFixed(2);
        bid.volume = e.target.value;
        // bid.volume = Number(e.target.value);
        updateBid(bid);
    }

    const priceChanged = (e) => {
        console.log(e.target.value);
        // bid.price_per_volume = Number(e.target.value).toFixed(2);
        bid.price_per_volume = e.target.value;
        // bid.price_per_volume = Number(e.target.value);
        updateBid(bid);
    }

    

    return (
        <TableRow key={share.pk}>
            <TableCell>
            <Link to={'/athletes/' + share.athlete.pk + '/'}>{share.athlete.name} </Link>
            {/* </TableCell>
            <TableCell> */}
                 ({share.volume})              </TableCell>
            <TableCell>
            <TextField label="Volume" size="small"
        value={bid.volume} 
        variant="outlined" 
        onChange={volumeChanged}
        style={{width: "70px", marginBottom: 10, marginRight: 10}}
        /> 
        <TextField label="Price" size="small"
        value={bid.price_per_volume} 
        variant="outlined" 
        onChange={priceChanged}
        style={{width: "70px"}}
        /></TableCell>
        <TableCell>{Number(bid.price_per_volume*bid.volume).toFixed(2) }</TableCell>
        </TableRow>
  );
}