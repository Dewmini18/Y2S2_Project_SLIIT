// import { MapPin, Star } from "lucide-react";
// import { Button } from "./ui/button";
import { useState } from "react";
import { Link } from 'react-router-dom';


function MedicineCard(props) {
  // let num = 1;
  //   const handleClick = () => {
  //     console.log("I was clicked")
  //     console.log("Inside handleclick", num)
  //     num = num + 1;
  //   }
  //   console.log("Outside handleclick", num)
//   const [num, setNum] = useState(0);

//   const handleClick = () => {
//     setNum(5);
//     console.log(num);
//     console.log("Hey");
//   };

  return (
    // <Link to={`/medicine/${props.medicine._id}`} className="card bg-base-100 w-96 shadow-sm">
    //     <figure>
    //         <img
    //         src="https://img.daisyui.com/images/stock/photo-1606107557195-0e29a4b5b4aa.webp"
    //         alt="Shoes" />
    //     </figure>
    //     <div className="card-body">
    //         <h2 className="card-title">
    //         {props.medicine.name}
    //         <div className="badge badge-secondary">NEW</div>
    //         </h2>
    //         <p>{props.medicine.description}</p>
    //         <div className="card-actions justify-end">
    //         <div className="badge badge-outline">{props.medicine.category}</div>
    //         </div>
    //     </div>
    // </Link>
    
    <Link to={`/medicine/${props.medicine._id}`} className="block group relative">
      <div className="relative aspect-[4/3] overflow-hidden rounded-xl">
        <img
          src={props.medicine.image}
          alt={props.medicine.name}
          className="object-cover w-full h-full absolute transition-transform group-hover:scale-105"
        />
      </div>
      <div className="mt-3 space-y-2">
        <h3 className="font-semibold text-lg">{props.medicine.name}</h3>
        <div className="flex items-center text-muted-foreground">
          {/* <MapPin className="h-4 w-4 mr-1" /> */}
          <span>{props.medicine.brand}</span>
        </div>
        <div className="flex items-baseline space-x-2">
          <span className="text-xl font-semibold">LKR {props.medicine.price}</span>
        </div>
      </div>
      {/* <div className="mt-2">
        <p className="text-red-500 text-3xl">{num}</p>
        <Button type="button" className={"w-full"} onClick={handleClick}>
          Click Me
        </Button>
      </div> */}
    </Link>
  );
}

export default MedicineCard;
